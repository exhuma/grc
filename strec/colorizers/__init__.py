import re
import sys
from abc import ABCMeta, abstractmethod
from os.path import basename, exists, join
from typing import Any, Dict, TextIO

from yaml import SafeLoader, load

from strec import CONF_LOCATIONS
from strec.exc import StrecException
from strec.garabik import Parser, parse_config


def find_conf(file_or_app_name):
    """
    Searches for a config file name.

    Search order:
        ~/.strec/conf.d/<appname>.yml
        /etc/strec/conf.d/<appname>.yml
        /usr/share/strec/conf.d/<appname>.yml

    TIP:
        If you have one config file that could be used for multiple
        applications: symlink it!
    """
    if exists(file_or_app_name):
        # TODO: This section covers filenames instead of command base-names. It
        #       should no longer be necessary as it is covered by
        #       Colorizer.from_basename
        return file_or_app_name

    for folder in CONF_LOCATIONS:
        confname = join(folder, "%s.yml" % file_or_app_name)
        if exists(confname):
            return confname
        confname = join(folder, "conf.%s" % file_or_app_name)
        if exists(confname):
            return confname

    sys.stderr.write(
        "No config found named '%s.yml'\n"
        "Resolution order:\n   %s\n"
        % (file_or_app_name, ",\n   ".join(CONF_LOCATIONS))
    )
    sys.exit(9)


class Colorizer(metaclass=ABCMeta):
    @abstractmethod
    def feed(self, line):  # pragma: no cover
        raise NotImplementedError("Not yet implemented")

    @staticmethod
    def from_basename(cmd_basename: str, output: TextIO, colors: Any):
        # TODO inline "find_conf" into this method
        filename = find_conf(cmd_basename)
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            return YamlColorizer.from_config_filename(filename, output, colors)
        if basename(filename).startswith("conf."):
            with open(filename) as fptr:
                rules = parse_config(fptr.read())
            return Parser(rules, output, colors)
        raise StrecException(f"Unknown config-type in {filename!r}")

    @staticmethod
    def from_config_filename(filename: str, output: TextIO, colors: Any):
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            return YamlColorizer.from_config_filename(filename, output, colors)
        if basename(filename).startswith("conf."):
            with open(filename) as fptr:
                rules = parse_config(fptr.read())
            return Parser(rules, output, colors)
        raise StrecException(f"Unknown config-type in {filename!r}")


class YamlColorizer(Colorizer):
    @staticmethod
    def from_config_filename(filename: str, output: TextIO, colors: Any):
        with open(filename) as fptr:
            conf = load(fptr, Loader=SafeLoader)
        return YamlColorizer(conf, output, colors)

    def __init__(
        self, conf: Dict[str, Any], output: TextIO, colors: Any
    ) -> None:
        self.state = ["root"]
        self.conf = conf
        self.output = output
        self.colors = colors

    def feed(self, line):

        for rule in self.conf[self.state[-1]]:
            # rule defaults
            regex = re.compile(rule.get("match", r"^.*$"))
            replace = rule.get("replace", r"\0")
            push = rule.get("push", None)
            pop = rule.get("pop", False)
            continue_ = rule.get("continue", False)

            # transform the line if necessary
            match = regex.search(line)
            if match:
                line = regex.sub(replace, line)
                line = line.format(**self.colors.DATA)
                if push:
                    self.state.append(push)
                if pop and len(self.state) > 1:
                    self.state.pop()

                if not continue_:
                    break
        self.output.write(line)
