import strec.garabik as g
import sys


class ANSI:
    @staticmethod
    def get(name: str) -> str:
        data = {
            "black": "\u001b[30m",
            "red": "\u001b[31m",
            "green": "\u001b[32m",
            "yellow": "\u001b[33m",
            "blue": "\u001b[34m",
            "magenta": "\u001b[35m",
            "cyan": "\u001b[36m",
            "white": "\u001b[37m",
            "reset": "\u001b[0m",
        }
        return data.get(name, "")


parser = g.Parser(
    [g.Rule(r"(\d{3})-(\w{3})-(\d{3})", ["blue", "green", "yellow"])],
    sys.stdout,
    ANSI,
)

for n in range(10):
    line = sys.stdin.readline()
    parser.feed(line)
