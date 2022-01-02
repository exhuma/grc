from io import StringIO
from unittest.mock import Mock, patch

import pytest

import strec.core as core


def test_process_lines():
    source = StringIO("hello-world")
    colorizer = Mock()
    core.process_lines(source, colorizer)
    colorizer.feed.assert_called_with("hello-world")


def test_create_stdin():
    with patch("strec.core.sys") as sys:
        source = core.create_stdin("ls")
    assert source == sys.stdin


def test_create_stdin_noconfig():
    """
    When reading from stdin, we don't know the command and must require a
    config
    """
    with patch("strec.core.sys") as sys:
        source = core.create_stdin("")
    sys.exit.assert_called_with(9)


@patch("strec.core.create_pty")
def test_run(create_pty):
    pytest.skip("TODO - YAML")
    output = StringIO()
    stream = StringIO("hello")
    create_pty.return_value = stream
    core.run(output, ["ls", "--", "-l"])
    create_pty.assert_called_with("ls", ["-l"])


@patch("strec.core.create_stdin")
def test_run_piped(create_stdin):
    pytest.skip("TODO - YAML")
    output = StringIO()
    stream = StringIO("hello")
    create_stdin.return_value = stream
    core.run(output, ["-c", "ls"])
    create_stdin.assert_called_with("ls")
