import sys
from abc import ABCMeta, abstractmethod
from os.path import basename, exists, join
from posixpath import expanduser
from typing import Iterable, TextIO, Tuple

import pkg_resources
from typing_extensions import Protocol

from strec.exc import StrecException

CONF_LOCATIONS = [
    join(expanduser("~"), ".strec", "conf.d"),
    join("/etc", "strec", "conf.d"),
    join("/usr", "share", "strec", "conf.d"),
]

# Add the installation folder to the config search path
CONF_LOCATIONS.append(pkg_resources.resource_filename("strec", "../configs"))


class ColorMap(Protocol):
    """
    The protocol used to map named colors to terminal control-characters
    """

    @staticmethod
    def get(name: str) -> str:
        ...

    @staticmethod
    def items() -> Iterable[Tuple[str, str]]:
        ...


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
    def from_basename(cmd_basename: str, output: TextIO, colors: ColorMap):
        from .garabik import GarabikColorizer
        from .yaml import YamlColorizer

        # TODO inline "find_conf" into this method
        filename = find_conf(cmd_basename)
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            return YamlColorizer.from_config_filename(filename, output, colors)
        if basename(filename).startswith("conf."):
            return GarabikColorizer.from_config_filename(
                filename, output, colors
            )
        raise StrecException(f"Unknown config-type in {filename!r}")

    @staticmethod
    def from_config_filename(filename: str, output: TextIO, colors: ColorMap):
        from .garabik import GarabikColorizer
        from .yaml import YamlColorizer

        if filename.endswith(".yml") or filename.endswith(".yaml"):
            return YamlColorizer.from_config_filename(filename, output, colors)
        if basename(filename).startswith("conf."):
            return GarabikColorizer.from_config_filename(
                filename, output, colors
            )
        raise StrecException(f"Unknown config-type in {filename!r}")
