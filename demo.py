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
    ],
    sys.stdout,
    g.ANSI,
)

for n in range(10):
    line = sys.stdin.readline()
    parser.feed(line)
