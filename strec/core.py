"""
Stream Coloriser

TODO
    - if no replacement is specified, emit the original line
    - Allow for pop "before" and "after"
"""

import subprocess as sp
import sys
from typing import IO, List, Optional

from strec.colorizers.base import Colorizer


def process_lines(source: IO[str], parser: Colorizer):
    """
    Read lines from *source* and process them until an empty-line is read.
    """
    while True:
        line = source.readline()
        if not line:
            break
        parser.feed(line)


def create_pty(args: List[str]) -> Optional[IO[str]]:
    proc = sp.Popen(args, stdout=sp.PIPE, text=True)
    return proc.stdout


def create_stdin(config_name: str) -> IO[str]:
    source = sys.stdin
    if not config_name:
        print(
            "ERROR: When parsing stdin, you need to specify a config file!",
            file=sys.stderr,
        )
        sys.exit(9)
    return source
