from os.path import expanduser, join
from warnings import warn

from .version import VERSION

__version__ = VERSION

CONF_LOCATIONS = [
    join(expanduser('~'), '.grc', 'conf.d'),
    join('/etc', 'grc', 'conf.d'),
    join('/usr', 'share', 'grc', 'conf.d')
]

warn("""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   grc will be renamed to "strec" soon
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

*This* grc is currently preventing the original grc to be published on pypi. To
make room, this version will be renamed to "strec" to a void any confusion

The new package "strec" is already available on pypi. And has been pulled in as
dependency for convenience.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
""")
