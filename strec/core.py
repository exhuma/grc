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

from strec import CONF_LOCATIONS
from strec.colorizers import Colorizer
from strec.garabik import ANSI, Parser, parse_config

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
    parser.add_argument(
        "cmd", help="The command to run and colorize.", nargs="*"
    )
    return parser.parse_args(args)


def find_conf(file_or_app_name):
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
    if exists(file_or_app_name):
        return file_or_app_name

    for folder in CONF_LOCATIONS:
        confname = join(folder, "%s.yml" % file_or_app_name)
        if exists(confname):
            if confname.endswith(".yml") or confname.endswith(".yaml"):
                raise NotImplementedError(
                    "YAML config files are not yet supported"
                )
            return confname

    sys.stderr.write(
        "No config found named '%s.yml'\n"
        "Resolution order:\n   %s\n"
        % (file_or_app_name, ",\n   ".join(CONF_LOCATIONS))
    )
    sys.exit(9)


def load_config(config_name):
    with open(find_conf(config_name)) as fptr:
        rules = parse_config(fptr.read())
    return rules


def process_lines(source, parser):
    """
    Read lines from *source* and process them until an empty-line is read.
    """
    while True:
        line = source.readline()
        if not line:
            break
        parser.feed(line)


def create_pty(cmd, args):
    cmd = basename(cmd)
    source = pexpect.spawn(" ".join([cmd] + args), maxread=1, encoding="utf8")
    return source


def create_stdin(config_name):
    source = sys.stdin
    if not config_name:
        print(
            "ERROR: When parsing stdin, you need to specify a config file!",
            file=sys.stderr,
        )
        sys.exit(9)
    return source


def run(stream, args):
    args = parse_args(args)

    if args.cmd:
        cmd = basename(args.cmd[0])
        rules = load_config(args.config_name or cmd)
        cmdargs = args.cmd[1:]
        source = create_pty(cmd, cmdargs)
    else:
        source = create_stdin(args.config_name)
        rules = load_config(args.config_name)

    parser = Parser(rules, stream, ANSI)
    process_lines(source, parser)


def main():  # pragma: no cover
    with open(sys.stdout.fileno(), "w", buffering=1) as stdout:
        run(stdout, None)


if __name__ == "__main__":  # pragma: no cover
    main()
