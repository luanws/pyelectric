import os
import traceback

from scripts import Script
from scripts.clear_build import clear_build


def publish():
    clear_build()
    try:
        os.system('python setup.py sdist bdist_wheel')  # build
        os.system('twine upload dist/*')  # publish
    finally:
        traceback.print_exc()
        clear_build()


class Deploy(Script):
    def __str__(self) -> str:
        return 'publish'

    def __call__(self):
        publish()
