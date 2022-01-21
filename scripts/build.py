import os

from scripts import Script


def build():
    os.system('python setup.py sdist bdist_wheel')


class Build(Script):
    def __str__(self) -> str:
        return 'build'

    def __call__(self):
        build()
