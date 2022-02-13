from pathlib import Path

import nonebot
from alembic.config import CommandLine, Config

nonebot.init()


class MyCommandLine(CommandLine):
    def main(self, argv=None):
        config_path = Path(__file__).parent / "alembic.ini"
        options = self.parser.parse_args(argv)
        if not hasattr(options, "cmd"):
            # see http://bugs.python.org/issue9253, argparse
            # behavior changed incompatibly in py3.3
            self.parser.error("too few arguments")
        else:
            cfg = Config(
                file_=str(config_path),
                ini_section=options.name,
                cmd_opts=options,
            )
            self.run_cmd(cfg, options)


def main(argv=None, prog=None, **kwargs):
    """The console runner function for Alembic."""
    MyCommandLine(prog=prog).main(argv)


if __name__ == "__main__":
    main(prog="datastore")
