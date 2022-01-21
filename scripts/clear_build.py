import shutil
from contextlib import suppress

from scripts import Script


def clear_build():
    folders = ['build', 'dist', 'pyelectric.egg-info']
    for folder in folders:
        with suppress(FileNotFoundError):
            shutil.rmtree(folder)


class ClearBuild(Script):
    def __str__(self) -> str:
        return 'clear build'

    def __call__(self):
        clear_build()
