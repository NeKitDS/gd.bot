from pathlib import Path
from typing import IO, Union

__all__ = ("assets", "load_asset")

assets = Path(__file__).parent / "assets"


def load_asset(path: Union[Path, str], read_raw: bool = False) -> IO:
    """Load asset from assets folder and return IO-like object.
    Do not forget to close it!

    Example:

        with load_asset("auto_epic.png", read_raw=True) as file:
            ...  # do something
    """
    mode = "rb" if read_raw else "r"
    return open(assets / path, mode)
