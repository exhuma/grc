from typing import Iterable

from typing_extensions import Protocol


class ColorMap(Protocol):
    """
    The protocol used to map named colors to terminal control-characters
    """

    @staticmethod
    def get(name: str) -> str:
        ...

    @staticmethod
    def keys() -> Iterable[str]:
        ...
