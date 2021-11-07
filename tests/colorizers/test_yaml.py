"""
Tests for the "strec"-style YAML based coloriser
"""
import pytest

import strec.core as core
from strec.colorizers import YamlColorizer


@pytest.fixture
def colorizer():
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
    coloriser = YamlColorizer(conf)
    yield coloriser


def test_stack_push(colorizer):
    """
    Make sure we push onto the stack if a line matches a pushing condition
    """
    line = colorizer.process("hello-world")
    assert colorizer.state == ["root", "new-state"]


def test_stack_pop(colorizer):
    """
    Make sure we pop from the stack if a line matches a popping condition
    """
    colorizer.state = ["root", "another-state"]
    line = colorizer.process("hello-world")
    assert colorizer.state == ["root"]


def test_process_line(colorizer):
    line = colorizer.process("hello-world")
    expected = "{t.blue}hello-world{t.normal}"
    assert line == expected
