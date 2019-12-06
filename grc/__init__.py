from os.path import expanduser, join

from .version import VERSION

__version__ = VERSION

CONF_LOCATIONS = [
    join(expanduser('~'), '.grc', 'conf.d'),
    join('/etc', 'grc', 'conf.d'),
    join('/usr', 'share', 'grc', 'conf.d')
]
