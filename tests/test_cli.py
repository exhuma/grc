import pytest

import strec.cli as cli


@pytest.mark.parametrize(
    "args, config_name, cmd",
    [
        (["-c", "foo", "cmd"], "foo", ["cmd"]),
        (["--config", "foo", "cmd"], "foo", ["cmd"]),
        (["cmd", "foo", "bar"], None, ["cmd", "foo", "bar"]),
    ],
)
def test_parse_args(args, config_name, cmd):
    result = cli.parse_args(args)
    assert result.config_name == config_name
    assert result.cmd == cmd
