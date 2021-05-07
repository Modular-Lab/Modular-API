# coding: utf-8
import asyncio
import logging
import threading
from pathlib import Path
from importlib import import_module

from fastapi import FastAPI

from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata
from sqlalchemy import create_engine
import pprint

from modularapi.settings import get_setting
from modularapi.db import db

logger = logging.getLogger()


if get_setting().LOG_TO_STDOUT:
    logging.basicConfig(
        level=get_setting().LOGGING_LEVEL,
        format=get_setting().LOGGING_FMT,
    )


def get_app():
    app = FastAPI()

    modules = tuple(p for p in Path().glob("modules/*") if p.is_dir())
    if not modules:
        logger.warning("There is no modules installed !")
    for module in modules:
        module_path = ".".join(module.parts)
        logger.info(f"loading module [{module_path}]")

        if not (module / "main.py").is_file():
            logger.error(f"Could not load module {module_path} missing main.py!")
            continue

        m = import_module(".".join([module_path, "main"]))
        on_load_hook = getattr(m, "on_load", None)
        if on_load_hook is not None:

            # check if it's an awaitable
            if asyncio.iscoroutinefunction(on_load_hook):
                t = threading.Thread(target=asyncio.run, args=[on_load_hook(app)])
                t.start()
                t.join()
                # todo raise the exception from the thread
            else:
                on_load_hook(app)

        # load "db.py" if it exists and it's a file
        if (module / "db.py").is_file():
            import_module(".".join([module_path, "db"]))

    # ensure the database is up to date
    engine = create_engine(get_setting().PG_DNS)
    mc = MigrationContext.configure(engine.connect())
    diff = compare_metadata(mc, db)
    if diff:
        logger.critical(
            f"The database is not up to date ! use the Modular cli to update the database schema {pprint.pformat(diff)}"
        )
        exit(1)

    db.init_app(app)
    return app
