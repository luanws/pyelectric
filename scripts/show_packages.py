import setuptools

from scripts import Script


def show_packages():
    packages = setuptools.find_packages(include=['pyelectric', 'pyelectric.*'])
    print('\n'.join(packages))


class ShowPackages(Script):
    def __str__(self) -> str:
        return 'show packages'

    def __call__(self):
        show_packages()
