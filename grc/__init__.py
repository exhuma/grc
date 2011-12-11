from os.path import expanduser, join

__version__='1.0b3'

CONF_LOCATIONS = [
    join(expanduser('~'), '.grc', 'conf.d'),
    join('/etc', 'grc', 'conf.d'),
    join('/usr', 'share', 'grc', 'conf.d')
    ]
