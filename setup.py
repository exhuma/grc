import os
from os.path import join

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
    long_description=open("docs/README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    install_requires = [],
    data_files=[
        ("/usr/share/grc/conf.d", [join('configs', _) for _ in
            os.listdir('configs') if _[-1] != '~'])
        ],
    scripts = ['grc/scripts/grc'],
    packages=find_packages(exclude=["tests.*", "tests"]),
    zip_safe=False,
)

