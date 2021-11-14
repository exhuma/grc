from io import StringIO
from textwrap import dedent

import pytest

import strec.garabik as garabik


class Colors:
    @staticmethod
    def get(name: str) -> str:
        data = {
            "blue": "<blue>",
            "red": "<red>",
            "yellow": "<yellow>",
            "reset": "<reset>",
            "default": "<reset>",
        }
        return data[name]


def test_color_list():
    input_data = "this is a hello something world string"
    expected = "this is a <blue>hello<reset> something <red>world<reset> string"
    output = StringIO()
    rules = [
        garabik.Rule(
            r"\b(hello) something (world)\b",
            ["blue", "red"],
            count=garabik.Count.MORE,
        ),
    ]

    parser = garabik.Parser(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


@pytest.mark.skip()
def test_color_list2():
    """
    What happens if the beginning of the string does not start with a matching
    group?
    """
    input_data = "this is a hello something world string"
    expected = "this is a <blue>hello<reset> something <red>world<reset> string"
    output = StringIO()
    rules = [
        garabik.Rule(
            r"beginning \b(hello) something (world)\b", ["blue", "red"]
        ),
    ]

    parser = garabik.Parser(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


def test_count_more():
    input_data = "this is a hello something world string"
    expected = "this is a <blue>hello<reset> something <red>world<reset> string"
    output = StringIO()
    rules = [
        garabik.Rule(
            r"\b(hello)\b",
            ["blue"],
            count=garabik.Count.MORE,
        ),
        garabik.Rule(
            r"\b(world)\b",
            ["red"],
            count=garabik.Count.MORE,
        ),
    ]

    parser = garabik.Parser(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


def test_count_stop():
    input_data = "this is a hello something world string"
    expected = "this is a <blue>hello<reset> something world string"
    output = StringIO()
    rules = [
        garabik.Rule(
            r"\b(hello)\b",
            ["blue"],
            count=garabik.Count.STOP,
        ),
        garabik.Rule(
            r"\b(world)\b",
            ["red"],
            count=garabik.Count.STOP,
        ),
    ]

    parser = garabik.Parser(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


def test_count_once():
    input_data = "hello world hello world hello world"
    expected = "hello <blue>world<reset> hello world hello world"
    output = StringIO()
    rules = [
        garabik.Rule(
            r"\b(world)\b",
            ["blue"],
            count=garabik.Count.ONCE,
        ),
    ]

    parser = garabik.Parser(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


def test_count_block():
    input_data = dedent(
        """\
        first line
        second line
        third line
        fourth line
        fifth line
        """
    )
    expected = dedent(
        """\
        first line
        <blue>second line<reset>
        <blue>third line
        <reset><reset>fourth line<reset>
        fifth line
        """
    )
    output = StringIO()
    rules = [
        garabik.Rule(
            r"\b(second line)\b",
            ["blue"],
            count=garabik.Count.BLOCK,
        ),
        garabik.Rule(
            r"\b(fourth line)\b",
            ["default"],
            count=garabik.Count.UNBLOCK,
        ),
    ]

    parser = garabik.Parser(rules, output, Colors)
    for line in input_data.splitlines(keepends=True):
        parser.feed(line)
    result = output.getvalue()
    assert result == expected


def test_skip():
    input_data = dedent(
        """\
        first line
        second line
        third line
        fourth line
        fifth line
        """
    )
    expected = dedent(
        """\
        first line
        second line
        fourth line
        fifth line
        """
    )
    output = StringIO()
    rules = [
        garabik.Rule(
            r"\b(third line)\b",
            ["blue"],
            count=garabik.Count.BLOCK,
            skip=True,
        ),
    ]

    parser = garabik.Parser(rules, output, Colors)
    for line in input_data.splitlines(keepends=True):
        parser.feed(line)
    result = output.getvalue()
    assert result == expected


def test_replace():
    input_data = dedent(
        """\
        first line
        second line
        third line
        fourth line
        fifth line
        """
    )
    expected = dedent(
        """\
        <blue><yellow>hello<reset> first <blue>world<reset> line
        <reset><blue><yellow>hello<reset> second <blue>world<reset> line
        <reset><blue><yellow>hello<reset> third <blue>world<reset> line
        <reset><blue><yellow>hello<reset> fourth <blue>world<reset> line
        <reset><blue><yellow>hello<reset> fifth <blue>world<reset> line
        <reset>"""
    )
    output = StringIO()
    rules = [
        garabik.Rule(
            r"\b(\w+) line\b",
            ["blue"],
            count=garabik.Count.MORE,
            replace=r"hello \1 world line",
        ),
        garabik.Rule(
            r"\b(hello)\b",
            ["yellow"],
            count=garabik.Count.MORE,
        ),
    ]

    parser = garabik.Parser(rules, output, Colors)
    for line in input_data.splitlines(keepends=True):
        parser.feed(line)
    result = output.getvalue()
    assert result == expected


def test_parse_config_multiple():
    """
    We want to be able to convert a config file into a list of rules.
    """
    config_content = dedent(
        r"""# Regular Up
        regexp=\sup(?: (\d+) days?,)? +(\d+ min|\d+:\d+)(?=,)
        colours=green,bold green, bold green
        -
        # users
        regexp=\b(\d+) users?
        colours=yellow,bold yellow
        -
        # load average
        regexp=load average: (\d+[\.,]\d+),\s(\d+[\.,]\d+),\s(\d+[\.,]\d+)
        colours=default,bright_cyan,cyan,dark cyan
        -
        # W Command section
        # Title
        regexp=^USER.*$
        colours=bold
        skip=false
        count=more
        """
    )
    rules = list(garabik.parse_config(config_content))
    expected = [
        garabik.Rule(
            r"\sup(?: (\d+) days?,)? +(\d+ min|\d+:\d+)(?=,)",
            ["green", "bold green", "bold green"],
        ),
        garabik.Rule(
            r"\b(\d+) users?",
            ["yellow", "bold yellow"],
        ),
        garabik.Rule(
            r"load average: (\d+[\.,]\d+),\s(\d+[\.,]\d+),\s(\d+[\.,]\d+)",
            ["default", "bright_cyan", "cyan", "dark cyan"],
        ),
        garabik.Rule(r"^USER.*$", ["bold"]),
    ]
    assert rules == expected


def test_parse_config_single():
    """
    We want to be able to convert a config file into a list of rules.
    """
    config_content = dedent(
        """# Regular Up
        regexp=\sup(?: (\d+) days?,)? +(\d+ min|\d+:\d+)(?=,)
        colours=green,bold green, bold green
        """
    )
    rules = list(garabik.parse_config(config_content))
    expected = [
        garabik.Rule(
            r"\sup(?: (\d+) days?,)? +(\d+ min|\d+:\d+)(?=,)",
            ["green", "bold green", "bold green"],
        ),
    ]
    assert rules == expected


def test_parse_config_empty():
    """
    We want to be able to convert a config file into a list of rules.
    """
    config_content = ""
    rules = list(garabik.parse_config(config_content))
    expected = []
    assert rules == expected
