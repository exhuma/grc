from os.path import expanduser, join

from .version import VERSION

__version__ = VERSION

CONF_LOCATIONS = [
    join(expanduser("~"), ".strec", "conf.d"),
    join("/etc", "strec", "conf.d"),
    join("/usr", "share", "strec", "conf.d"),
]
