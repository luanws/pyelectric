import os
import shutil
import traceback
from contextlib import suppress

import setuptools
from pymenu import Menu


def clear_build():
    folders = ['build', 'dist', 'pyelectric.egg-info']
    for folder in folders:
        with suppress(FileNotFoundError):
            shutil.rmtree(folder)


def show_packages():
    print(setuptools.find_packages())


def deploy():
    clear_build()
    try:
        os.system('python setup.py sdist bdist_wheel')
        os.system('twine upload dist/*')
    finally:
        traceback.print_exc()
        clear_build()


menu = Menu('Scripts')
menu.add_options([
    ('build', lambda: os.system('python setup.py sdist bdist_wheel')),
    ('publish', lambda: os.system('twine upload dist/*')),
    ('clear build', clear_build),
    ('show packages', show_packages),
    ('deploy', deploy),
])
menu.show()
