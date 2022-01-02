import sys
from strec.garabik import parse_config, ANSI, Parser

with open(sys.argv[1]) as fptr:
    config = fptr.read()

rules = list(parse_config(config))
parser = Parser(rules, sys.stdout, ANSI)

for line in sys.stdin.readlines():
    parser.feed(line)
