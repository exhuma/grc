"""
This module defines a parser for config files from
https://github.com/garabik/grc
"""
from enum import Enum
import re
from dataclasses import dataclass
from typing import Callable, List, Protocol, TextIO

UNCHANGED = "unchanged"


class ColorMap(Protocol):
    """
    The protocol used to map named colors to terminal control-characters
    """

    @staticmethod
    def get(name: str) -> str:
        ...


class Count(Enum):
    MORE = "more"
    STOP = "stop"


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
    """
    A coloring rule from ``garabik/grc``
    """

    regex: str
    colors: List[str]
    count: Count


def make_matcher(
    colors: List[str], color_map: ColorMap
) -> Callable[[re.Match[str]], str]:
    """
    Create a function that converts a :py:class:`re.Match` object into a
    colorised string.

    This function can be used by :py:func:`re.sub`

    :param colors: The colors used for replacement.
    :param color_map: The definition of the special control-characters for the
        colors to use.
    """

    def replace_match(match: re.Match[str]) -> str:
        """
        Create a colorised string from a :py:class:`re.Match` object.
        """
        full_text = match.group(0)
        offset = match.start(0)
        output = full_text[: match.start(1) - offset]
        for i in range(1, len(match.groups()) + 1):
            end_position = None
            if i < len(match.groups()):
                end_position = match.start(i + 1) - offset
            if colors[i - 1] == UNCHANGED:
                replacement = match.group(i)
            else:
                replacement = f"{color_map.get(colors[i - 1])}{match.group(i)}{color_map.get('reset')}"
            output += replacement
            output += full_text[match.end(i) - offset : end_position]
        return output

    return replace_match


class Parser:
    """
    The main implementation to process input lines and convert them to text
    with the appropriate control-characters.
    """

    def __init__(
        self, rules: List[Rule], output: TextIO, colors: ColorMap
    ) -> None:
        self.rules = rules
        self.output = output
        self.colors = colors

    def feed(self, line: str) -> None:
        output = line
        for rule in self.rules:
            output = re.sub(
                rule.regex, make_matcher(rule.colors, self.colors), output
            )
            if rule.count == Count.STOP:
                break
        self.output.write(output)
