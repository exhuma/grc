import os
from os.path import exists, join

from setuptools import find_packages, setup


def get_version():
    # type: () -> str
    '''
    Retrieves the version information for this package.
    '''
    filename = 'strec/version.py'

    with open(filename) as fptr:
        # pylint: disable=invalid-name, exec-used
        obj = compile(fptr.read(), filename, 'single')
        data = {}  # type: ignore
        exec(obj, data)
    return data['VERSION']


PACKAGE = "strec"
NAME = "strec"
DESCRIPTION = "Generic Coloriser"
with open('docs/README.rst') as fptr:
    LONG_DESCRIPTION = fptr.read()
AUTHOR = "Michel Albert"
AUTHOR_EMAIL = "michel@albert.lu"
VERSION = get_version()

if os.geteuid() == 0:
    CONF_TARGET = "/usr/share/strec/conf.d"
else:
    from os.path import join, expanduser
    CONF_TARGET = join(expanduser('~'), '.strec', 'conf.d')

if not exists(CONF_TARGET):
    os.makedirs(CONF_TARGET)
    print('Created folder for config files: %r' % CONF_TARGET)

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    install_requires=[
        'blessings',
        'pexpect',
        'pyyaml',
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
        ]
    },
    entry_points={
        'console_scripts': [
            'strec=strec.core:main'
        ]
    },
    data_files=[
        (CONF_TARGET, [join('configs', _) for _ in
                       os.listdir('configs') if _[-1] != '~'])
    ],
    packages=find_packages(exclude=["tests.*", "tests"]),
    zip_safe=False,
)
