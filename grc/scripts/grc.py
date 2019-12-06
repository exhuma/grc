#!/usr/bin/env python -u

"""
Generic Colorizer

TODO
    - if no replacement is specified, emit the original line
    - Allow for pop "before" and "after"
"""

import re
import sys
from optparse import OptionParser
from os.path import basename, exists, join

import pexpect
import pkg_resources
from yaml import SafeLoader, load

from blessings import Terminal
from grc import CONF_LOCATIONS

STATE = ['root']

# Add the installation folder to the config search path
CONF_LOCATIONS.append(pkg_resources.resource_filename('grc', '../configs'))


def parse_options():
    '''
    Returns a tuple of command-line options and remaining arguments (see
    optparse)
    '''
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config_name",
                      help="Use NAME as config-name. Overrides auto-detection. The file should exist in the folders searched for configs. See :meth:find_conf(name)",
                      metavar="NAME")
    return parser.parse_args()


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

    sys.stderr.write("No config found named '%s.yml'\n"
                     'Resolution order:\n   %s\n' % (
                         appname,
                         ',\n   '.join(CONF_LOCATIONS)))
    sys.exit(9)


def run(stream):
    options, args = parse_options()
    term = Terminal()
    cols = term.width or 80

    if args:
        config_name = options.config_name or basename(args[0])
        source = pexpect.spawn(" ".join(args), cols=cols, maxread=1)
    else:
        source = sys.stdin
        if not options.config_name:
            print('${t.red}ERROR:${t.normal} When parsing stdin, you need to '
                  'specify a config file!'.format(t=term), file=sys.stderr)
            sys.exit(9)
        config_name = options.config_name

    with open(find_conf(config_name)) as fptr:
        conf = load(fptr, Loader=SafeLoader)

    while True:
        line = source.readline()
        if not line:
            break
        for rule in conf[STATE[-1]]:
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
                    STATE.append(push)
                if pop and len(STATE) > 1:
                    STATE.pop()

                if not continue_:
                    break

        stream.write(line.format(t=term))


def main():
    with open(sys.stdout.fileno(), 'w', buffering=1) as stdout:
        run(stdout)


if __name__ == '__main__':
    main()
