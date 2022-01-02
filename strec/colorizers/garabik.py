"""
This module defines a parser for config files from
https://github.com/garabik/grc
"""
import re
from array import array
from dataclasses import dataclass
from enum import Enum
from typing import IO, Any, Dict, Iterable, List, Pattern, Tuple

from strec.colorizers.base import Colorizer
from strec.themes import ColorMap

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


class Count(Enum):
    MORE = "more"
    STOP = "stop"
    ONCE = "once"
    BLOCK = "block"
    UNBLOCK = "unblock"


@dataclass
class Rule:
    """
    A coloring rule from ``garabik/grc``
    """

    # TODO: Might make sense to use a compiled pattern
    regex: Pattern[str]
    colors: List[str]
    count: Count = Count.MORE
    skip: bool = False
    replace: str = ""

    def matches(self, line: str) -> bool:
        """
        Returns True if the line matches this rule.
        """
        return bool(re.search(self.regex, line))


def convert(key: str, value: str) -> Tuple[str, Any]:
    if key in {"colour", "colours", "color", "colors"}:
        return "colours", [item.strip() for item in value.split(",")]
    if key == "count":
        return key, Count(value)
    if key == "skip":
        return key, value.lower() == "true"
    if key == "regexp":
        pattern = re.compile(value)
        return key, pattern
    return key, value


def parse_config(config_content: str) -> list[Rule]:
    rule_options: Dict[str, Any] = {}
    output: List[Rule] = []
    for line in config_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        key, value = convert(key, value)

        if RULE_SEPARATOR.fullmatch(line[0]):
            output.append(Rule(**rule_options))
            rule_options.clear()
        else:
            rule_options[CONFIG_KEY_MAP.get(key, key)] = value

    if rule_options:
        output.append(Rule(**rule_options))
    return output


def apply_replacements(text: str, replacements: List[Replacement]) -> str:
    buffer = array("u", text)
    # Python bug? Applying only "reversed" is not sufficient! Must also call "sorted"
    for rpl in reversed(sorted(replacements)):
        buffer[rpl.span] = array("u", rpl.text)
    return buffer.tounicode()


def get_replacements(
    match: re.Match[str], rule: Rule, colors: ColorMap
) -> Iterable[Replacement]:
    for group_index in range(1, len(match.groups()) + 1):
        if match.group(group_index) is None:
            continue
        slc = slice(*match.span(group_index))
        clr = rule.colors[group_index - 1]
        yield Replacement(
            slc,
            f"{colors.get(clr)}{match.string[slc]}{colors.get('reset')}",
        )


class GarabikColorizer(Colorizer):
    """
    The main implementation to process input lines and convert them to text
    with the appropriate control-characters.
    """

    def __init__(
        self, rules: List[Rule], output: IO[str], colors: ColorMap
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
            if rule.replace and rule.matches(output):
                output = rule.regex.sub(rule.replace, output)

            matches = rule.regex.finditer(output)
            for match in matches:
                replacements.extend(get_replacements(match, rule, self.colors))
                if rule.count == Count.ONCE:
                    break

            if rule.count == Count.STOP:
                break
            elif rule.matches(output) and rule.count == Count.BLOCK:
                self.block_color = rule.colors[0]
        output = apply_replacements(output, replacements)
        self.output.write(output)

    @staticmethod
    def from_config_filename(
        filename: str, output: IO[str], colors: ColorMap
    ) -> "GarabikColorizer":
        with open(filename) as fptr:
            rules = parse_config(fptr.read())
        return GarabikColorizer(rules, output, colors)
