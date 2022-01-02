import sys
from argparse import ArgumentParser, Namespace
from os.path import basename
from typing import IO, List, Optional

from strec.colorizers import Colorizer
from strec.core import create_pty, create_stdin, process_lines
from strec.themes.ansi import ANSI


def parse_args(args: Optional[List[str]]) -> Namespace:
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


def run(stream: IO[str], args: Optional[List[str]]) -> None:
    parsed_args = parse_args(args)

    if parsed_args.cmd:
        cmd = basename(parsed_args.cmd[0])
        parser = Colorizer.from_basename(
            parsed_args.config_name or cmd, stream, ANSI
        )
        source = create_pty(parsed_args.cmd)
    else:
        parser = Colorizer.from_config_filename(
            parsed_args.config_name, stream, ANSI
        )
        source = create_stdin(parsed_args.config_name)

    if source is None:
        sys.stderr.write("Unexpected error when opening the text input")
        return
    process_lines(source, parser)


def main():  # pragma: no cover
    with open(sys.stdout.fileno(), "w", buffering=1) as stdout:
        run(stdout, None)
