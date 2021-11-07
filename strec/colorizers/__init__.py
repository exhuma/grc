import re
from abc import ABCMeta, abstractmethod
from os.path import exists, join

from yaml import SafeLoader, load

from strec import CONF_LOCATIONS


class Colorizer(metaclass=ABCMeta):
    @abstractmethod
    def process(self, line):
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

    @staticmethod
    def find_conf(appname):
        """
        Searches for a config file name.

        Search order:
            ~/.grc/conf.d/<appname>.yml
            /etc/grc/conf.d/<appname>.yml
            /usr/share/grc/conf.d/<appname>.yml

        TIP:
            If you have one config file that could be used for multiple
            applications: symlink it!
        """
        for folder in CONF_LOCATIONS:
            confname = join(folder, "%s.yml" % appname)
            if exists(confname):
                return confname

        raise FileNotFoundError(
            "No config found named '%s.yml'\n"
            "Resolution order:\n   %s\n"
            % (appname, ",\n   ".join(CONF_LOCATIONS))
        )

    def __init__(self, conf):
        self.state = ["root"]
        self.conf = conf

    def process(self, line):

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
        return line


class Garabik(Colorizer):
    @staticmethod
    def load(filename):
        lines = []
        sections = []
        current_section = {
            "regexp": "",
            "colours": [],
            "count": "more",
            "command": "",
            "skip": False,
            "replace": False,
            "concat": "",
        }
        allowed_keys = current_section.keys()
        with open(filename) as fptr:
            for line_no, line in enumerate(fptr, 1):
                if line.strip().startswith("#") or not line.strip():
                    continue
                if re.match(r"^[-=]+$", line.strip()):
                    sections.append(current_section)
                    current_section = {
                        "regexp": "",
                        "colours": [],
                        "count": "more",
                        "command": "",
                        "skip": False,
                        "replace": False,
                        "concat": "",
                    }
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key not in allowed_keys:
                    raise ValueError(
                        "Invalid key (%r) found in file %r at "
                        "line %d. Valid keys are: %r"
                        % (key, filename, line_no, allowed_keys)
                    )
                if key == "regexp":
                    current_section[key] = re.compile(value)
                else:
                    current_section[key] = value
        return Garabik(sections)

    @staticmethod
    def from_config(filename):
        return Garabik.load(filename)

    def __init__(self, rules):
        self.state = ["root"]
        self.rules = rules

    def process(self, line):
        for rule in self.rules:
            match = re.match(rule["regexp"], line)
            if match:
                re.sub
        return "*" + line
