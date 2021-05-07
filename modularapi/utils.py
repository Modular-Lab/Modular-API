# coding: utf-8
from pathlib import Path

from alembic.config import Config


class AlembicConfig(Config):
    def get_template_directory(self):
        pkg_dir = Path(__file__).resolve().parent
        return pkg_dir / "templates"


# from https://stackoverflow.com/a/2656405
def _on_rmtree_error(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    import os

    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise exc_info
