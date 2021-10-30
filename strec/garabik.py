from dataclasses import dataclass
from typing import Any, Callable, List, TextIO
import re


class ColorMap(Protocol):
    """
    The protocol used to map named colors to terminal control-characters
    """

    @staticmethod
    def get(name: str) -> str:
        ...


class ANSI:
    """
    A simple implementation for ANSI color codes.
    """

    @staticmethod
    def get(name: str) -> str:
        data = {
            "black": "\x1b[30m",
            "red": "\x1b[31m",
            "green": "\x1b[32m",
            "yellow": "\x1b[33m",
            "blue": "\x1b[34m",
            "magenta": "\x1b[35m",
            "cyan": "\x1b[36m",
            "white": "\x1b[37m",
            "reset": "\x1b[0m",
        }
        return data.get(name, "")


@dataclass
class Rule:
    regex: str
    colors: List[str]




def make_matcher(rule: Rule, colors):
    def replace_match(match: re.Match):
        full_text = match.group(0)
        offset = match.start(0)
        output = full_text[: match.start(1) - offset]
        for i in range(1, len(match.groups()) + 1):
            end_position = None
            if i < len(match.groups()):
                end_position = match.start(i + 1) - offset
            replacement = (
                f"{colors.get(rule.colors[i - 1])}{match.group(i)}{colors.get('reset')}"
            )
            output += replacement
            output += full_text[match.end(i) - offset : end_position]
        return output

    return replace_match


class Parser:
    def __init__(self, rules: List[Rule], output: TextIO, colors: Any) -> None:
        self.rules = rules
        self.output = output
        self.colors = colors

    def feed(self, line: str) -> None:
        for rule in self.rules:
            output = re.sub(rule.regex, make_matcher(rule, self.colors), line)
            self.output.write(output)
