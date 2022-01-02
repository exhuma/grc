from typing import Dict, Iterable

from typing_extensions import Protocol


class ColorMap(Protocol):
    """
    The protocol used to map named colors to terminal control-characters
    """

    DATA: Dict[str, str]

    @staticmethod
    def get(name: str) -> str:
        ...

    @staticmethod
    def keys() -> Iterable[str]:
        ...
