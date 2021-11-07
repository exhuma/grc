import sys

import strec.garabik as g

parser = g.Parser(
    [
        g.Rule(
            r"(\d{3})-(\w{3})-(\d{3})",
            ["blue", "unchanged", "yellow"],
            g.Count.MORE,
        ),
        g.Rule(
            r"(\d{3})-(\w{3})-(\d{3})",
            ["blue", "unchanged", "yellow"],
            g.Count.MORE,
        ),
        g.Rule(
            r"(block begin)",
            ["yellow"],
            g.Count.BLOCK,
        ),
        g.Rule(
            r"(block end)",
            ["default"],
            g.Count.UNBLOCK,
        ),
        g.Rule(
            r"\b(\w+) line\b",
            ["blue"],
            count=g.Count.MORE,
            replace=r"hello \1 world line",
        ),
        g.Rule(
            r"(line)",
            ["yellow"],
            count=g.Count.MORE,
        ),
    ],
    sys.stdout,
    g.ANSI,
)

for n in range(30):
    line = sys.stdin.readline()
    parser.feed(line)
