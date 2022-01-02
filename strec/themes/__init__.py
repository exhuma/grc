from typing import Iterable, Mapping

from typing_extensions import Protocol


class ColorMap(Protocol):
    """
    The protocol used to map named colors to terminal control-characters
    """

    DATA: Mapping[str, str]

    @staticmethod
    def get(name: str) -> str:
        ...

    @staticmethod
    def keys() -> Iterable[str]:
        ...
