try:
    import bot  # type: ignore
except ImportError:
    import nonebot

    nonebot.init()

from alembic.config import main

if __name__ == "__main__":
    main(prog="datastore")
