from unittest.mock import patch, Mock

import pytest
from io import StringIO
import strec.core as core


@pytest.mark.parametrize(
    "args, config_name, cmd",
    [
        (["-c", "foo", "cmd"], "foo", ["cmd"]),
        (["--config", "foo", "cmd"], "foo", ["cmd"]),
        (["cmd", "foo", "bar"], None, ["cmd", "foo", "bar"]),
    ],
)
def test_parse_args(args, config_name, cmd):
    result = core.parse_args(args)
    assert result.config_name == config_name
    assert result.cmd == cmd


def test_find_config_existing():
    with patch("strec.core.exists") as exists:
        exists.return_value = True
        result = core.find_conf("testapp")
    assert result.endswith("testapp.yml")


def test_find_config_missing():
    with patch("strec.core.sys") as sys:
        result = core.find_conf("testapp")
    sys.exit.assert_called_with(9)


def test_process_lines():
    source = StringIO("hello-world")
    output = StringIO()
    colorizer = Mock()
    colorizer.process.return_value = "sentinel"
    core.process_lines(source, colorizer, output, None)
    result = output.getvalue()
    assert result == "sentinel"
    colorizer.process.assert_called_with("hello-world")


def test_create_pty():
    with patch("strec.core.pexpect") as pexpect:
        core.create_pty("ls", ["-l"])
    pexpect.spawn.assert_called_with("ls -l", maxread=1, encoding="utf8")


def test_create_stdin():
    with patch("strec.core.sys") as sys:
        source = core.create_stdin("ls", None)
    assert source == sys.stdin


def test_create_stdin_noconfig():
    """
    When reading from stdin, we don't know the command and must require a
    config
    """
    with patch("strec.core.sys") as sys:
        source = core.create_stdin("", Mock())
    sys.exit.assert_called_with(9)


@patch("strec.core.Terminal")
@patch("strec.core.create_pty")
def test_run(create_pty, terminal):
    output = StringIO()
    stream = StringIO("hello")
    create_pty.return_value = stream
    result = core.run(output, ["ls", "--", "-l"])
    create_pty.assert_called_with("ls", ["-l"])


@patch("strec.core.Terminal")
@patch("strec.core.create_stdin")
def test_run_piped(create_stdin, terminal):
    output = StringIO()
    stream = StringIO("hello")
    create_stdin.return_value = stream
    result = core.run(output, ["-c", "ls"])
    create_stdin.assert_called_with("ls", terminal())
