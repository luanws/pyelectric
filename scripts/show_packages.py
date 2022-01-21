import setuptools

from scripts import Script


def show_packages():
    print('\n'.join(setuptools.find_packages()))


class ShowPackages(Script):
    def __str__(self) -> str:
        return 'show packages'

    def __call__(self):
        show_packages()
