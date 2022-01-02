import sys
from abc import ABCMeta, abstractmethod
from os import environ
from os.path import basename, exists, join
from posixpath import expanduser
from typing import IO, Optional

import pkg_resources

from strec.exc import StrecException
from strec.themes import ColorMap

CONF_LOCATIONS = [
    join(expanduser("~"), ".strec", "conf.d"),
    join("/etc", "strec", "conf.d"),
    join("/usr", "share", "strec", "conf.d"),
]

# Prepend config-folder specified as environment variable
if "STREC_CONFIG_PATH" in environ:
    CONF_LOCATIONS.insert(0, environ["STREC_CONFIG_PATH"])

# Add the installation folder to the config search path
CONF_LOCATIONS.append(pkg_resources.resource_filename("strec", "../configs"))


def find_conf(file_or_app_name: str) -> str:
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
    return ""


class Colorizer(metaclass=ABCMeta):
    @abstractmethod
    def feed(self, line: str) -> None:  # pragma: no cover
        raise NotImplementedError("Not yet implemented")

    @staticmethod
    def from_basename(
        cmd_basename: str, output: IO[str], colors: ColorMap
    ) -> Optional["Colorizer"]:
        from .garabik import GarabikColorizer
        from .yaml import YamlColorizer

        filename = find_conf(cmd_basename)
        if not filename:
            return None
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            return YamlColorizer.from_config_filename(filename, output, colors)
        if basename(filename).startswith("conf."):
            return GarabikColorizer.from_config_filename(
                filename, output, colors
            )
        raise StrecException(f"Unknown config-type in {filename!r}")

    @staticmethod
    def from_config_filename(
        filename: str, output: IO[str], colors: ColorMap
    ) -> "Colorizer":
        from .garabik import GarabikColorizer
        from .yaml import YamlColorizer

        if filename.endswith(".yml") or filename.endswith(".yaml"):
            return YamlColorizer.from_config_filename(filename, output, colors)
        if basename(filename).startswith("conf."):
            return GarabikColorizer.from_config_filename(
                filename, output, colors
            )
        raise StrecException(f"Unknown config-type in {filename!r}")
