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

import pkg_resources

import pexpect
from grc import CONF_LOCATIONS
from grc.term import TerminalController
from yaml import load

STATE = ['root']

LINE_BUFFERED = open(sys.stdout.fileno(), 'w', buffering=1)

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

def main():
    options, args = parse_options()
    term = TerminalController()
    cols = term.COLS or 80

    if args:
        config_name = options.config_name or basename(args[0])
        source = pexpect.spawn(" ".join(args), cols=cols, maxread=1)
    else:
        source = sys.stdin
        if not options.config_name:
            print(term.render('${RED}ERROR:${NORMAL} When parsing stdin, you need to specify a config file!'), file=sys.stderr)
            sys.exit(9)
        config_name = options.config_name

    conf = load(open(find_conf(config_name)))
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

        LINE_BUFFERED.write(term.render(line))

if __name__ == '__main__':
    main()
