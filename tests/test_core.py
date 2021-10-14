from unittest.mock import patch, Mock

import pytest
from io import StringIO
import strec.core as core


@pytest.fixture
def fresh_state():
    try:
        core.STATE = ["root"]
        yield
    finally:
        core.STATE = ["root"]


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


def test_find_config_existing(fresh_state):
    with patch("strec.core.exists") as exists:
        exists.return_value = True
        result = core.find_conf("testapp")
    assert result.endswith("testapp.yml")


def test_find_config_missing(fresh_state):
    with patch("strec.core.sys") as sys:
        result = core.find_conf("testapp")
    sys.exit.assert_called_with(9)


def test_process_line(fresh_state):
    conf = core.load_config("ls")
    line = core.process_line("drwxr-xr-x 3 exhuma exhuma 4096 Oct 14 07:19 tests", conf)
    expected = (
        "{t.blue}drwxr-xr-x{t.normal} {t.yellow}3{t.normal} exhuma "
        "exhuma {t.yellow}4096{t.normal} Oct {t.yellow}14{t.normal} "
        "{t.yellow}07{t.normal}:{t.yellow}19{t.normal} tests"
    )
    assert line == expected


def test_stack_push(fresh_state):
    """
    Make sure we push onto the stack if a line matches a pushing condition
    """
    conf = {
        "root": [
            {
                "match": "(hello-world)",
                "push": "new-state",
            },
        ]
    }
    line = core.process_line("hello-world", conf)
    assert core.STATE == ["root", "new-state"]


def test_stack_pop(fresh_state):
    """
    Make sure we pop from the stack if a line matches a popping condition
    """
    conf = {
        "another-state": [
            {
                "match": "(hello-world)",
                "pop": True,
            },
        ]
    }
    core.STATE = ["root", "another-state"]
    line = core.process_line("hello-world", conf)
    assert core.STATE == ["root"]


def test_process_lines(fresh_state):
    source = StringIO("hello-world")
    output = StringIO()
    conf = {
        "root": [
            {
                "match": "(hello-world)",
                "replace": ">\\1<",
            },
        ]
    }
    core.process_lines(source, output, conf, None)
    result = output.getvalue()
    assert result == ">hello-world<"


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
