#!/usr/bin/env python -u

"""
Generic Colorizer

TODO
    - if no replacement is specified, emit the original line
    - Allow for pop "before" and "after"
"""

import re
import sys
from argparse import ArgumentParser
from os.path import basename, exists, join

import pexpect
import pkg_resources
from yaml import SafeLoader, load

from blessings import Terminal
from strec import CONF_LOCATIONS

STATE = ["root"]

# Add the installation folder to the config search path
CONF_LOCATIONS.append(pkg_resources.resource_filename("strec", "../configs"))


def parse_args(args):
    """
    Returns a tuple of command-line options and remaining arguments (see
    optparse)
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        dest="config_name",
        help=(
            "Use NAME as config-name. Overrides auto-detection. The file "
            "should exist in the folders searched for configs."
        ),
        metavar="NAME",
    )
    parser.add_argument("cmd", help="The command to run and colorize.", nargs="*")
    return parser.parse_args(args)


def find_conf(appname):
    """
    Searches for a config file name.

    Search order:
        ~/.strec/conf.d/<appname>.yml
        /etc/strec/conf.d/<appname>.yml
        /usr/share/strec/conf.d/<appname>.yml

    TIP:
        If you have one config file that could be used for multiple
        applications: symlink it!
    """
    for folder in CONF_LOCATIONS:
        confname = join(folder, "%s.yml" % appname)
        if exists(confname):
            return confname

    sys.stderr.write(
        "No config found named '%s.yml'\n"
        "Resolution order:\n   %s\n" % (appname, ",\n   ".join(CONF_LOCATIONS))
    )
    sys.exit(9)


def process_line(line, conf):
    for rule in conf[STATE[-1]]:
        # rule defaults
        regex = re.compile(rule.get("match", r"^.*$"))
        replace = rule.get("replace", r"\0")
        push = rule.get("push", None)
        pop = rule.get("pop", False)
        continue_ = rule.get("continue", False)

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
    return line


def load_config(config_name):
    with open(find_conf(config_name)) as fptr:
        conf = load(fptr, Loader=SafeLoader)
    return conf


def process_lines(source, stream, conf, term):
    """
    Read lines from *source* and process them until an empty-line is read.
    """
    while True:
        line = source.readline()
        if not line:
            break
        line = process_line(line, conf)
        stream.write(line.format(t=term))


def create_pty(cmd, args):
    cmd = basename(cmd)
    source = pexpect.spawn(" ".join([cmd] + args), maxread=1, encoding="utf8")
    return source


def create_stdin(config_name, term):
    source = sys.stdin
    if not config_name:
        print(
            "${t.red}ERROR:${t.normal} When parsing stdin, you need to "
            "specify a config file!".format(t=term),
            file=sys.stderr,
        )
        sys.exit(9)
    return source


def run(stream, args):
    args = parse_args(args)
    term = Terminal()

    if args.cmd:
        cmd = basename(args.cmd[0])
        config_name = args.config_name or cmd
        cmdargs = args.cmd[1:]
        source = create_pty(cmd, cmdargs)
    else:
        source = create_stdin(args.config_name, term)
        config_name = args.config_name

    conf = load_config(config_name)

    process_lines(source, stream, conf, term)


def main():  # pragma: no cover
    with open(sys.stdout.fileno(), "w", buffering=1) as stdout:
        run(stdout, None)


if __name__ == "__main__":  # pragma: no cover
    main()
