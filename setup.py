import os
from os.path import exists, join

from setuptools import find_packages, setup

PACKAGE = "grc"
NAME = "grc"
DESCRIPTION = "Generic Colorizer"
AUTHOR = "Michel Albert"
AUTHOR_EMAIL = "michel@albert.lu"
VERSION = __import__(PACKAGE).__version__

if os.geteuid() == 0:
    CONF_TARGET = "/usr/share/grc/conf.d"
else:
    from os.path import join, expanduser
    CONF_TARGET = join(expanduser('~'), '.grc', 'conf.d')

if not exists(CONF_TARGET):
    os.makedirs(CONF_TARGET)
    print('Created folder for config files: %r' % CONF_TARGET)

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("docs/README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    install_requires = [
        'blessings',
        'pexpect',
        'pyyaml',
    ],
    entry_points = {
        'console_scripts': [
            'grc=grc.scripts.grc:main'
        ]
    },
    data_files=[
        (CONF_TARGET, [join('configs', _) for _ in
            os.listdir('configs') if _[-1] != '~'])
        ],
    packages=find_packages(exclude=["tests.*", "tests"]),
    zip_safe=False,
)
