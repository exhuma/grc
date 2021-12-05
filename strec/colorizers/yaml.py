import re
from typing import Any, Dict, TextIO

from yaml import SafeLoader, load

from strec.colorizers.base import Colorizer
from strec.themes import ColorMap


class YamlColorizer(Colorizer):
    @staticmethod
    def from_config_filename(filename: str, output: TextIO, colors: ColorMap):
        with open(filename) as fptr:
            conf = load(fptr, Loader=SafeLoader)
        return YamlColorizer(conf, output, colors)

    def __init__(
        self, conf: Dict[str, Any], output: TextIO, colors: ColorMap
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
