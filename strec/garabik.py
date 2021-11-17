"""
This module defines a parser for config files from
https://github.com/garabik/grc
"""
import re
from array import array
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Generator, List, Protocol, TextIO

UNCHANGED = "unchanged"
RULE_SEPARATOR = re.compile(r"[^a-z0-9]", re.IGNORECASE)
CONFIG_KEY_MAP = {
    "colours": "colors",
    "regexp": "regex",
}


@dataclass(order=True)
class Replacement:
    span: slice
    text: str


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
    ONCE = "once"
    BLOCK = "block"
    UNBLOCK = "unblock"


class ANSI:
    """
    A simple implementation for ANSI color codes.
    """

    @staticmethod
    def get(name: str) -> str:
        data = {
            "none": "",
            "default": "\033[0m",
            "reset": "\033[0m",
            "bold": "\033[1m",
            "underline": "\033[4m",
            "blink": "\033[5m",
            "reverse": "\033[7m",
            "concealed": "\033[8m",
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            "on_black": "\033[40m",
            "on_red": "\033[41m",
            "on_green": "\033[42m",
            "on_yellow": "\033[43m",
            "on_blue": "\033[44m",
            "on_magenta": "\033[45m",
            "on_cyan": "\033[46m",
            "on_white": "\033[47m",
            "beep": "\007",
            "previous": "prev",
            "unchanged": "",
            # non-standard attributes, supported by some terminals
            "dark": "\033[2m",
            "italic": "\033[3m",
            "rapidblink": "\033[6m",
            "strikethrough": "\033[9m",
            # aixterm bright color codes
            # prefixed with standard ANSI codes for graceful failure
            "bright_black": "\033[30;90m",
            "bright_red": "\033[31;91m",
            "bright_green": "\033[32;92m",
            "bright_yellow": "\033[33;93m",
            "bright_blue": "\033[34;94m",
            "bright_magenta": "\033[35;95m",
            "bright_cyan": "\033[36;96m",
            "bright_white": "\033[37;97m",
            "on_bright_black": "\033[40;100m",
            "on_bright_red": "\033[41;101m",
            "on_bright_green": "\033[42;102m",
            "on_bright_yellow": "\033[43;103m",
            "on_bright_blue": "\033[44;104m",
            "on_bright_magenta": "\033[45;105m",
            "on_bright_cyan": "\033[46;106m",
            "on_bright_white": "\033[47;107m",
        }
        names = name.split()
        out = [data.get(n, "") for n in names]
        return "".join(out)


@dataclass
class Rule:
    """
    A coloring rule from ``garabik/grc``
    """

    # TODO: Might make sense to use a compiled pattern
    regex: str
    colors: List[str]
    count: Count = Count.MORE
    skip: bool = False
    replace: str = ""

    def matches(self, line: str) -> bool:
        """
        Returns True if the line matches this rule.
        """
        return bool(re.search(self.regex, line))


def convert(key: str, value: str) -> Any:
    if key == "colours":
        return [item.strip() for item in value.split(",")]
    if key == "count":
        return Count(value)
    if key == "skip":
        return value.lower() == "true"
    return value


def parse_config(config_content: str) -> list[Rule]:
    rule_options = {}
    output = []
    for line in config_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        value = convert(key, value)

        if RULE_SEPARATOR.fullmatch(line[0]):
            output.append(Rule(**rule_options))
            rule_options.clear()
        else:
            rule_options[CONFIG_KEY_MAP.get(key, key)] = value

    if rule_options:
        output.append(Rule(**rule_options))
    return output


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
        output: List[str] = []
        # Keep a track of the end of each group because we need to copy the
        # characters which sit in between the groups into the resulting output
        end_of_group = match.start(0)
        for group_index, (grp, color) in enumerate(
            zip(match.groups(), colors), start=1
        ):
            print(f"      {group_index} {grp!r} {color}")
            span = slice(*match.span(group_index))
            if span.start == -1:
                continue
            if end_of_group:
                output.append(match.string[end_of_group : span.start])
            output.append(
                f"{color_map.get(color)}{grp}{color_map.get('reset')}"
            )
            end_of_group = span.stop
        output.append(match.string[end_of_group : match.end(0)])
        return "".join(output)

        # TODO: the garabik conf for "ls" contains an group with "unchanged"
        #       color as first element. But running it through upstream
        #       garabik/grc still colorises that group which is not in line with
        #       re.sub()
        1 / 0

        return match.expand("foo >\\1< bar")

        full_text = match.group(0)
        offset = match.start(0)
        for i in range(1, len(match.groups()) + 1):
            end_position = None

        return output

    return replace_match


def apply_replacements(text: str, replacements: List[Replacement]) -> str:
    buffer = array("u", text)
    # Python bug? Applying only "reversed" is not sufficient! Must also call "sorted"
    for rpl in reversed(sorted(replacements)):
        buffer[rpl.span] = array("u", rpl.text)
    return buffer.tounicode()


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
        self.block_color = ""

    def feed(self, line: str) -> None:
        output = line

        for rule in self.rules:
            if rule.matches(line) and rule.skip:
                return

        if self.block_color != "":
            for rule in self.rules:
                if rule.matches(line) and rule.count == Count.UNBLOCK:
                    self.block_color = ""

        if self.block_color != "":
            output = f"{self.colors.get(self.block_color)}{line}{self.colors.get('reset')}"
            self.output.write(output)
            return

        replacements: List[Replacement] = []
        for rule in self.rules:
            count = 1 if rule.count == Count.ONCE else 0

            if rule.replace and rule.matches(output):
                output = re.sub(rule.regex, rule.replace, output)

            match = re.search(rule.regex, output)
            if match:
                for group_index in range(1, len(match.groups()) + 1):
                    if match.group(group_index) is None:
                        continue
                    slc = slice(*match.span(group_index))
                    clr = rule.colors[group_index - 1]
                    replacements.append(
                        Replacement(
                            slc,
                            f"{self.colors.get(clr)}{match.string[slc]}{self.colors.get('reset')}",
                        )
                    )

            if rule.count == Count.STOP:
                break
            elif rule.matches(output) and rule.count == Count.BLOCK:
                self.block_color = rule.colors[0]
        output = apply_replacements(output, replacements)
        self.output.write(output)
