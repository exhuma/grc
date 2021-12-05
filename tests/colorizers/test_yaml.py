"""
Tests for the "strec"-style YAML based coloriser
"""
from io import StringIO
from unittest.mock import patch

import pytest

import strec.core as core
from strec.colorizers import YamlColorizer


class DirectMapping(dict):
    def __getitem__(self, __k):
        return f"<{__k}>"


@pytest.fixture
def colorizer():
    colors = DirectMapping()
    conf = {
        "root": [
            {
                "match": "(hello-world)",
                "push": "new-state",
                "replace": r"{t.blue}\1{t.normal}",
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


def test_stack_push(colorizer):
    """
    Make sure we push onto the stack if a line matches a pushing condition
    """
    _, colorizer = colorizer
    colorizer.feed("hello-world")
    assert colorizer.state == ["root", "new-state"]


def test_stack_pop(colorizer):
    """
    Make sure we pop from the stack if a line matches a popping condition
    """
    _, colorizer = colorizer
    colorizer.state = ["root", "another-state"]
    colorizer.feed("hello-world")
    assert colorizer.state == ["root"]


def test_process_line(colorizer):
    output, colorizer = colorizer
    colorizer.feed("hello-world")
    expected = "{t.blue}hello-world{t.normal}"
    assert output.getvalue() == expected
