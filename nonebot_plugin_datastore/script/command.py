"""直接将 Alembic 的代码抄过来，然后改成异步

version: 1.9.2
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from alembic.autogenerate.api import RevisionContext
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from alembic.util.exc import AutogenerateDiffsDetected, CommandError
from alembic.util.messaging import obfuscate_url_pw
from sqlalchemy.util.langhelpers import asbool

from .utils import run_migration

if TYPE_CHECKING:
    from alembic.config import Config
    from alembic.runtime.environment import ProcessRevisionDirectiveFn
    from alembic.script.base import Script


async def revision(
    config: Config,
    message: str | None = None,
    autogenerate: bool = False,
    sql: bool = False,
    head: str = "head",
    splice: bool = False,
    branch_label: str | None = None,
    version_path: str | None = None,
    rev_id: str | None = None,
    depends_on: str | None = None,
    process_revision_directives: ProcessRevisionDirectiveFn | None = None,
) -> Script | None | list[Script | None]:
    """Create a new revision file.

    :param config: a :class:`.Config` object.

    :param message: string message to apply to the revision; this is the
     ``-m`` option to ``alembic revision``.

    :param autogenerate: whether or not to autogenerate the script from
     the database; this is the ``--autogenerate`` option to
     ``alembic revision``.

    :param sql: whether to dump the script out as a SQL string; when specified,
     the script is dumped to stdout.  This is the ``--sql`` option to
     ``alembic revision``.

    :param head: head revision to build the new revision upon as a parent;
     this is the ``--head`` option to ``alembic revision``.

    :param splice: whether or not the new revision should be made into a
     new head of its own; is required when the given ``head`` is not itself
     a head.  This is the ``--splice`` option to ``alembic revision``.

    :param branch_label: string label to apply to the branch; this is the
     ``--branch-label`` option to ``alembic revision``.

    :param version_path: string symbol identifying a specific version path
     from the configuration; this is the ``--version-path`` option to
     ``alembic revision``.

    :param rev_id: optional revision identifier to use instead of having
     one generated; this is the ``--rev-id`` option to ``alembic revision``.

    :param depends_on: optional list of "depends on" identifiers; this is the
     ``--depends-on`` option to ``alembic revision``.

    :param process_revision_directives: this is a callable that takes the
     same form as the callable described at
     :paramref:`.EnvironmentContext.configure.process_revision_directives`;
     will be applied to the structure generated by the revision process
     where it can be altered programmatically.   Note that unlike all
     the other parameters, this option is only available via programmatic
     use of :func:`.command.revision`

    """

    script_directory = ScriptDirectory.from_config(config)

    command_args = {
        "message": message,
        "autogenerate": autogenerate,
        "sql": sql,
        "head": head,
        "splice": splice,
        "branch_label": branch_label,
        "version_path": version_path,
        "rev_id": rev_id,
        "depends_on": depends_on,
    }
    revision_context = RevisionContext(
        config,
        script_directory,
        command_args,
        process_revision_directives=process_revision_directives,
    )

    environment = asbool(config.get_main_option("revision_environment"))

    if autogenerate:
        environment = True

        if sql:
            raise CommandError(
                "Using --sql with --autogenerate does not make any sense"
            )

        def retrieve_migrations(rev, context):
            revision_context.run_autogenerate(rev, context)
            return []

    elif environment:

        def retrieve_migrations(rev, context):
            revision_context.run_no_autogenerate(rev, context)
            return []

    elif sql:
        raise CommandError(
            "Using --sql with the revision command when "
            "revision_environment is not configured does not make any sense"
        )

    if environment:
        with EnvironmentContext(
            config,
            script_directory,
            fn=retrieve_migrations,  # type: ignore
            as_sql=sql,
            template_args=revision_context.template_args,
            revision_context=revision_context,
        ):
            await run_migration()

        # the revision_context now has MigrationScript structure(s) present.
        # these could theoretically be further processed / rewritten *here*,
        # in addition to the hooks present within each run_migrations() call,
        # or at the end of env.py run_migrations_online().

    scripts = list(revision_context.generate_scripts())
    if len(scripts) == 1:
        return scripts[0]
    else:
        return scripts


async def check(
    config: Config,
) -> None:
    """Check if revision command with autogenerate has pending upgrade ops.

    :param config: a :class:`.Config` object.

    .. versionadded:: 1.9.0

    """

    script_directory = ScriptDirectory.from_config(config)

    command_args = {
        "message": None,
        "autogenerate": True,
        "sql": False,
        "head": "head",
        "splice": False,
        "branch_label": None,
        "version_path": None,
        "rev_id": None,
        "depends_on": None,
    }
    revision_context = RevisionContext(
        config,
        script_directory,
        command_args,
    )

    def retrieve_migrations(rev, context):
        revision_context.run_autogenerate(rev, context)
        return []

    with EnvironmentContext(
        config,
        script_directory,
        fn=retrieve_migrations,
        as_sql=False,
        template_args=revision_context.template_args,
        revision_context=revision_context,
    ):
        await run_migration()

    # the revision_context now has MigrationScript structure(s) present.

    migration_script = revision_context.generated_revisions[-1]
    diffs = migration_script.upgrade_ops.as_diffs()  # type: ignore
    if diffs:
        raise AutogenerateDiffsDetected(f"New upgrade operations detected: {diffs}")
    else:
        config.print_stdout("No new upgrade operations detected.")


async def upgrade(
    config: Config,
    revision: str,
    sql: bool = False,
    tag: str | None = None,
) -> None:
    """Upgrade to a later version.

    :param config: a :class:`.Config` instance.

    :param revision: string revision target or range for --sql mode

    :param sql: if True, use ``--sql`` mode

    :param tag: an arbitrary "tag" that can be intercepted by custom
     ``env.py`` scripts via the :meth:`.EnvironmentContext.get_tag_argument`
     method.

    """

    script = ScriptDirectory.from_config(config)

    starting_rev = None
    if ":" in revision:
        if not sql:
            raise CommandError("Range revision not allowed")
        starting_rev, revision = revision.split(":", 2)

    def upgrade(rev, context):
        return script._upgrade_revs(revision, rev)

    with EnvironmentContext(
        config,
        script,
        fn=upgrade,
        as_sql=sql,
        starting_rev=starting_rev,
        destination_rev=revision,
        tag=tag,
    ):
        await run_migration()


async def downgrade(
    config: Config,
    revision: str,
    sql: bool = False,
    tag: str | None = None,
) -> None:
    """Revert to a previous version.

    :param config: a :class:`.Config` instance.

    :param revision: string revision target or range for --sql mode

    :param sql: if True, use ``--sql`` mode

    :param tag: an arbitrary "tag" that can be intercepted by custom
     ``env.py`` scripts via the :meth:`.EnvironmentContext.get_tag_argument`
     method.

    """

    script = ScriptDirectory.from_config(config)
    starting_rev = None
    if ":" in revision:
        if not sql:
            raise CommandError("Range revision not allowed")
        starting_rev, revision = revision.split(":", 2)
    elif sql:
        raise CommandError("downgrade with --sql requires <fromrev>:<torev>")

    def downgrade(rev, context):
        return script._downgrade_revs(revision, rev)

    with EnvironmentContext(
        config,
        script,
        fn=downgrade,
        as_sql=sql,
        starting_rev=starting_rev,
        destination_rev=revision,
        tag=tag,
    ):
        await run_migration()


async def history(
    config: Config,
    rev_range: str | None = None,
    verbose: bool = False,
    indicate_current: bool = False,
) -> None:
    """List changeset scripts in chronological order.

    :param config: a :class:`.Config` instance.

    :param rev_range: string revision range

    :param verbose: output in verbose mode.

    :param indicate_current: indicate current revision.

    """
    base: str | None
    head: str | None
    script = ScriptDirectory.from_config(config)
    if rev_range is not None:
        if ":" not in rev_range:
            raise CommandError(
                "History range requires [start]:[end], " "[start]:, or :[end]"
            )
        base, head = rev_range.strip().split(":")
    else:
        base = head = None

    environment = (
        asbool(config.get_main_option("revision_environment")) or indicate_current
    )

    def _display_history(config, script, base, head, currents=()):
        for sc in script.walk_revisions(base=base or "base", head=head or "heads"):
            if indicate_current:
                sc._db_current_indicator = sc.revision in currents

            config.print_stdout(
                sc.cmd_format(
                    verbose=verbose,
                    include_branches=True,
                    include_doc=True,
                    include_parents=True,
                )
            )

    async def _display_history_w_current(config, script, base, head):
        def _display_current_history(rev, context):
            if head == "current":
                _display_history(config, script, base, rev, rev)
            elif base == "current":
                _display_history(config, script, rev, head, rev)
            else:
                _display_history(config, script, base, head, rev)
            return []

        with EnvironmentContext(config, script, fn=_display_current_history):
            await run_migration()

    if base == "current" or head == "current" or environment:
        await _display_history_w_current(config, script, base, head)
    else:
        _display_history(config, script, base, head)


def heads(config, verbose=False, resolve_dependencies=False):
    """Show current available heads in the script directory.

    :param config: a :class:`.Config` instance.

    :param verbose: output in verbose mode.

    :param resolve_dependencies: treat dependency version as down revisions.

    """

    script = ScriptDirectory.from_config(config)
    if resolve_dependencies:
        heads = script.get_revisions("heads")
    else:
        heads = script.get_revisions(script.get_heads())

    for rev in heads:
        config.print_stdout(
            rev.cmd_format(verbose, include_branches=True, tree_indicators=False)  # type: ignore
        )


async def current(config: Config, verbose: bool = False) -> None:
    """Display the current revision for a database.

    :param config: a :class:`.Config` instance.

    :param verbose: output in verbose mode.

    """

    script = ScriptDirectory.from_config(config)

    def display_version(rev, context):
        if verbose:
            config.print_stdout(
                "Current revision(s) for %s:",
                obfuscate_url_pw(context.connection.engine.url),
            )
        for rev in script.get_all_current(rev):
            config.print_stdout(rev.cmd_format(verbose))  # type: ignore

        return []

    with EnvironmentContext(config, script, fn=display_version, dont_mutate=True):
        await run_migration()
