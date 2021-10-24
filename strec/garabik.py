from dataclasses import dataclass
from typing import Any, Callable, List, TextIO
import re


@dataclass
class Rule:
    regex: str
    colors: List[str]


def rule_2_sub(rule: Rule, color: Any) -> str:
    p = re.compile(rule.regex)

    items = [
        f"{color.get(rule.colors[n-1])}\\{n}{color.get('reset')}"
        for n in range(1, p.groups + 1)
    ]
    return items


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
