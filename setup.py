import os
from os.path import join, exists

from setuptools import setup, find_packages

PACKAGE = "grc"
NAME = "grc"
DESCRIPTION = "Generic Colorizer"
AUTHOR = "Michel Albert"
AUTHOR_EMAIL = "michel@albert.lu"
VERSION = __import__(PACKAGE).__version__
CONF_FOLDER = None

for folder in reversed(__import__(PACKAGE).CONF_LOCATIONS):
    if not exists(folder):
        try:
            os.makedirs(folder)
        except OSError:
            # Try the next folder
            continue
    CONF_FOLDER = folder

if not CONF_FOLDER:
    raise UserWarning("Unable to find a writable location for the config files")

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
        (CONF_FOLDER, [join('configs', _) for _ in
            os.listdir('configs') if _[-1] != '~'])
        ],
    scripts = ['grc/scripts/grc'],
    packages=find_packages(exclude=["tests.*", "tests"]),
    zip_safe=False,
)

print "***"
print "*** Config files have been stored in %s" % CONF_FOLDER
print "***"
