import sys
from argparse import ArgumentParser
from os.path import basename

from strec.colorizers import Colorizer
from strec.core import create_pty, create_stdin, process_lines
from strec.themes.ansi import ANSI


def parse_args(args):
    """
    Returns a tuple of command-line options and remaining arguments (see
    optparse)
    """
    parser = ArgumentParser(
        description=(
            "Colorise any text-stream by either reading from stdin or "
            "calling a process in a subshell, applying coloring rules via "
            "regexes and writing back the colorised output"
        )
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_name",
        help=(
            "Use NAME as config-name. Overrides auto-detection. This can "
            "either point to an existing file, or a simple relative filename. "
            "In the latter case the filename is looked up in bundled "
            "config-files."
        ),
        metavar="NAME",
    )
    parser.add_argument(
        "cmd",
        help=(
            "The command to run and colorize. Some shells may require "
            "separating this with a '--' from the strec command (f.ex. "
            "'strec -c <conf-file> -- ls -l'). If run like this, strec is able "
            "to auto-detect the colorisation file. As an alternative, strec "
            "can also read from stding in which case this argument is "
            "redundant."
        ),
        nargs="*",
    )
    return parser.parse_args(args)


def run(stream, args):
    args = parse_args(args)

    if args.cmd:
        cmd = basename(args.cmd[0])
        parser = Colorizer.from_basename(args.config_name or cmd, stream, ANSI)
        source = create_pty(args.cmd)
    else:
        parser = Colorizer.from_config_filename(args.config_name, stream, ANSI)
        source = create_stdin(args.config_name)

    process_lines(source, parser)


def main():  # pragma: no cover
    with open(sys.stdout.fileno(), "w", buffering=1) as stdout:
        run(stdout, None)