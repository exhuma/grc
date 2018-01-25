import re
from yaml import SafeLoader, load
from os.path import exists, join

from grc import CONF_LOCATIONS


class Colorizer:

    @staticmethod
    def from_config(config_name):
        filename = Colorizer.find_conf(config_name)
        with open(filename) as fptr:
            conf = load(fptr, Loader=SafeLoader)
        return Colorizer(conf)

    @staticmethod
    def from_basename(basename):
        filename = Colorizer.find_conf(basename)
        with open(filename) as fptr:
            conf = load(fptr, Loader=SafeLoader)
        return Colorizer(conf)

    @staticmethod
    def find_conf(appname):
        """
        Searches for a config file name.

        Search order:
            ~/.grc/conf.d/<appname>.yml
            /etc/grc/conf.d/<appname>.yml
            /usr/share/grc/conf.d/<appname>.yml

        TIP:
            If you have one config file that could be used for multiple
            applications: symlink it!
        """
        for folder in CONF_LOCATIONS:
            confname = join(folder, "%s.yml" % appname)
            if exists(confname):
                return confname

        raise FileNotFoundError("No config found named '%s.yml'\n"
                                'Resolution order:\n   %s\n' % (
                                    appname,
                                    ',\n   '.join(CONF_LOCATIONS)))

    def __init__(self, conf):
        self.state = ['root']
        self.conf = conf

    def process(self, line):

        for rule in self.conf[self.state[-1]]:
            # rule defaults
            regex = re.compile(rule.get('match', r'^.*$'))
            replace = rule.get('replace', r'\0')
            push = rule.get('push', None)
            pop = rule.get('pop', False)
            continue_ = rule.get('continue', False)

            # transform the line if necessary
            match = regex.search(line)
            if match:
                line = regex.sub(replace, line)
                if push:
                    self.state.append(push)
                if pop and len(self.state) > 1:
                    self.state.pop()

                if not continue_:
                    break
        return line
