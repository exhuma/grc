import re
from abc import ABCMeta, abstractmethod
from os.path import exists, join
from typing import Any, Dict, TextIO

from yaml import SafeLoader, load

import strec
from strec import CONF_LOCATIONS


class Colorizer(metaclass=ABCMeta):
    @abstractmethod
    def feed(self, line):  # pragma: no cover
        raise NotImplementedError("Not yet implemented")

    @staticmethod
    def from_basename(cmd_basename):
        # TODO detect garabic-style config
        return YamlColorizer.from_config(cmd_basename)

    @staticmethod
    def from_config(config_name):
        # TODO detect garabic-style config
        return YamlColorizer.from_config(config_name)


class YamlColorizer(Colorizer):
    @staticmethod
    def from_config(config_name):
        filename = YamlColorizer.find_conf(config_name)
        with open(filename) as fptr:
            conf = load(fptr, Loader=SafeLoader)
        return YamlColorizer(conf)

    @staticmethod
    def from_basename(basename):
        filename = YamlColorizer.find_conf(basename)
        with open(filename) as fptr:
            conf = load(fptr, Loader=SafeLoader)
        return YamlColorizer(conf)

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
                if push:
                    self.state.append(push)
                if pop and len(self.state) > 1:
                    self.state.pop()

                if not continue_:
                    break
        self.output.write(line)
