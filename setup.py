
from setuptools import setup, find_packages

PACKAGE = "grc"
NAME = "grc"
DESCRIPTION = "Generic Colorizer"
AUTHOR = "Michel Albert"
AUTHOR_EMAIL = "michel@albert.lu"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    install_requires = [
        'pyyaml'
      ],
    scripts = ['grc/scripts/grc'],
    packages=find_packages(exclude=["tests.*", "tests"]),
    zip_safe=False,
)

