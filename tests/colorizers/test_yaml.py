"""
Tests for the "strec"-style YAML based coloriser
"""
from io import StringIO
from typing import Tuple

import pytest

from strec.colorizers.yaml import YamlColorizer
from strec.themes.ansi import ANSI


class TestColors(ANSI):

    DATA = {
        "blue": "<blue>",
        "reset": "<reset>",
    }


@pytest.fixture
def colorizer_fixture():
    colors = TestColors
    conf = {
        "root": [
            {
                "match": "(hello-world)",
                "push": "new-state",
                "replace": r"{blue}\1{reset}",
            },
        ],
        "another-state": [
            {
                "match": "(hello-world)",
                "pop": True,
            },
        ],
    }
    output = StringIO()
    coloriser = YamlColorizer(conf, output, colors)
    yield output, coloriser


def test_stack_push(colorizer_fixture: Tuple[StringIO, YamlColorizer]):
    """
    Make sure we push onto the stack if a line matches a pushing condition
    """
    _, colorizer = colorizer_fixture
    colorizer.feed("hello-world")
    assert colorizer.state == ["root", "new-state"]


def test_stack_pop(colorizer_fixture: Tuple[StringIO, YamlColorizer]):
    """
    Make sure we pop from the stack if a line matches a popping condition
    """
    _, colorizer = colorizer_fixture
    colorizer.state = ["root", "another-state"]
    colorizer.feed("hello-world")
    assert colorizer.state == ["root"]


def test_process_line(colorizer_fixture: Tuple[StringIO, YamlColorizer]):
    output, colorizer = colorizer_fixture
    colorizer.feed("hello-world")
    expected = "<blue>hello-world<reset>"
    assert output.getvalue() == expected
