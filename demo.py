import strec.garabik as g
import sys


parser = g.Parser(
    [g.Rule(r"(\d{3})-(\w{3})-(\d{3})", ["blue", "green", "yellow"])],
    sys.stdout,
    g.ANSI,
)

for n in range(10):
    line = sys.stdin.readline()
    parser.feed(line)
