import re
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
            "cyan": "<cyan>",
            "bold magenta": "<bold magenta>",
            "reset": "<reset>",
            "default": "<reset>",
            "unchanged": "<unchanged>",
        }
        return data.get(name, "")


def test_color_list():
    input_data = "the quick brown fox jumps over the lazy dog"
    expected = (
        "the <blue>quick<reset> brown <red>fox<reset> jumps over the lazy dog"
    )
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"\b(quick) brown (fox)\b"),
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
            re.compile(r"beginning \b(hello) something (world)\b"),
            ["blue", "red"],
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
            re.compile(r"\b(hello)\b"),
            ["blue"],
            count=garabik.Count.MORE,
        ),
        garabik.Rule(
            re.compile(r"\b(world)\b"),
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
            re.compile(r"\b(hello)\b"),
            ["blue"],
            count=garabik.Count.STOP,
        ),
        garabik.Rule(
            re.compile(r"\b(world)\b"),
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
            re.compile(r"\b(world)\b"),
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
            re.compile(r"\b(second line)\b"),
            ["blue"],
            count=garabik.Count.BLOCK,
        ),
        garabik.Rule(
            re.compile(r"\b(fourth line)\b"),
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
            re.compile(r"\b(third line)\b"),
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
        <yellow>hello<reset> first <blue>world<reset> line
        <yellow>hello<reset> second <blue>world<reset> line
        <yellow>hello<reset> third <blue>world<reset> line
        <yellow>hello<reset> fourth <blue>world<reset> line
        <yellow>hello<reset> fifth <blue>world<reset> line
        """
    )
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"\b(\w+) line\b"),
            ["blue"],
            count=garabik.Count.MORE,
            replace=r"hello \1 world line",
        ),
        garabik.Rule(
            re.compile(r"\b(hello)\b"),
            ["yellow"],
            count=garabik.Count.MORE,
        ),
    ]

    parser = garabik.Parser(rules, output, Colors)
    for line in input_data.splitlines(keepends=True):
        parser.feed(line)
    result = output.getvalue()
    print(result)
    assert result == expected


def test_ungrouped_text():
    """
    If a regex contains ungrouped text, this text should be copied unmodified to
    the output.
    """
    line = "the quick brown fox"
    expected = "the quick <blue>brown<reset> fox"
    output = StringIO()
    rules = [
        garabik.Rule(
            re.compile(r"quick (\w+) fox"),
            ["blue"],
            count=garabik.Count.MORE,
        ),
    ]

    parser = garabik.Parser(rules, output, Colors)
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
            re.compile(r"\sup(?: (\d+) days?,)? +(\d+ min|\d+:\d+)(?=,)"),
            ["green", "bold green", "bold green"],
        ),
        garabik.Rule(
            re.compile(r"\b(\d+) users?"),
            ["yellow", "bold yellow"],
        ),
        garabik.Rule(
            re.compile(
                r"load average: (\d+[\.,]\d+),\s(\d+[\.,]\d+),\s(\d+[\.,]\d+)"
            ),
            ["default", "bright_cyan", "cyan", "dark cyan"],
        ),
        garabik.Rule(re.compile(r"^USER.*$"), ["bold"]),
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
            re.compile(r"\sup(?: (\d+) days?,)? +(\d+ min|\d+:\d+)(?=,)"),
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


def test_unmatched_regex_group():
    """
    If a rule regex has a capturing group, but that group does not match on a
    given line, the output should not be moodified for that group.
    """
    line = "-rw-rw-r-- 1 streamer streamer  344 Nov  7 17:52 CHANGELOG.rst\n"
    rule = garabik.Rule(
        regex=re.compile(
            "([A-Z][a-z]{2})\\s([ 1-3]\\d)\\s(?:([0-2]?\\d):([0-5]\\d)(?=[\\s,]|$)|\\s*(\\d{4}))"
        ),
        colors=["cyan", "cyan", "cyan", "cyan", "bold magenta"],
        count=garabik.Count.MORE,
        skip=False,
        replace="",
    )
    expected = (
        "-rw-rw-r-- 1 streamer streamer  344 <cyan>Nov<reset> <cyan> 7<reset> "
        "<cyan>17<reset>:<cyan>52<reset> CHANGELOG.rst\n"
    )
    output = StringIO()
    rules = [rule]
    parser = garabik.Parser(rules, output, Colors)
    parser.feed(line)
    assert output.getvalue() == expected


@pytest.mark.skip()
def test_something():  # TODO: rename test
    rules = list(
        garabik.parse_config(
            dedent(
                r"""
                regexp=(-|[a-z])(r)
                colours=blue,yellow
                """
            )
        )
    )
    line = "-rw-rwar--\n"
    expected = "<blue>-<reset><yellow>r<reset>w<blue>-<reset><yellow>r<reset>w<blue>a<reset><yellow>r<reset>--\n"
    output = StringIO()
    parser = garabik.Parser(rules, output, Colors)
    parser.feed(line)
    print("Result:", repr(output.getvalue()))
    assert output.getvalue() == expected
    1 / 0


@pytest.mark.skip()
def test_else():  # TODO: rename test
    rules = list(
        # XXX garabik.parse_config(
        # XXX     dedent(
        # XXX         r"""
        # XXX         regexp=([A-Z][a-z]{2})\s([ 1-3]\d)\s(?:([0-2]?\d):([0-5]\d)(?=[\s,]|$)|\s*(\d{4}))
        # XXX         colours=unchanged,cyan,cyan,cyan,cyan,bold magenta
        # XXX         """
        # XXX     )
        # XXX )
        garabik.parse_config(
            dedent(
                r"""
                regexp=(drwx)(rwx)r-x
                colours=cyan,yellow
                ----
                regexp=(?=(streamer) (streamer) (4096))
                colours=unchanged,red,blue
                """
            )
        )
    )
    line = "drwxrwxr-x 4 streamer streamer 4096 Nov 16 09:20 strec\n"
    output = StringIO()
    parser = garabik.Parser(rules, output, Colors)
    parser.feed(line)
    print("Result:", repr(output.getvalue()))
    1 / 0


@pytest.mark.skip()
def test_another():  # TODO: rename test
    rules = list(
        garabik.parse_config(
            dedent(
                r"""
                regexp=([A-Z][a-z]{2})\s([ 1-3]\d)\s(?:([0-2]?\d):([0-5]\d)(?=[\s,]|$)|\s*(\d{4}))
                colours=cyan,cyan,cyan,cyan,bold magenta
                """
            )
        )
    )
    line1 = "drwxrwxr-x 4 streamer streamer 4096 Nov 16  1996 strec\n"
    line2 = "drwxrwxr-x 4 streamer streamer 4096 Nov 16 09:20 strec\n"
    expected = (
        "drwxrwxr-x 4 streamer streamer 4096 "
        "<cyan>Nov<reset> <cyan>16<reset> <cyan>09<reset>:<cyan>20<reset> "
        "strec\n"
    )
    output = StringIO()
    parser = garabik.Parser(rules, output, Colors)
    parser.feed(line2)
    print("Result:", repr(output.getvalue()))
    assert output.getvalue() == expected
    1 / 0


@pytest.mark.skip("TODO")
def test_upstream_ls():
    line = "drwxrwxr-x 3 streamer streamer 4096 Nov  7 17:52 docs\n"
    with open("conf.ls") as fptr:
        rules = garabik.parse_config(fptr.read())
    output = StringIO()
    parser = garabik.Parser(rules, output, Colors)
    parser.feed(line)
    print(output.getvalue())
    1 / 0


def test_lookbehind():
    """
    If an earlier rule adds color-codes, lookbehinds should not break

    This is a behaviour of the old "grc" and should not be broken if we want to
    keep the config compatible.
    """
    line = "the quick brown fox jumps over the lazy dog"
    rules = garabik.parse_config(
        dedent(
            r"""
            regexp=brown (fox)
            colours=blue
            ---
            regexp=(?<=fox)\s(jumps)
            colours=cyan
            """
        )
    )
    output = StringIO()
    parser = garabik.Parser(rules, output, Colors)
    parser.feed(line)
    result = output.getvalue()
    expected = (
        "the quick brown <blue>fox<reset> <cyan>jumps<reset> over the lazy dog"
    )
    assert result == expected
