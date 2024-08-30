from re import search
from typing import Optional, Tuple


def hex_to_rgb(hex: str) -> Optional[Tuple[int, ...]]:
    if hex is None or len(hex) < 6:
        return None

    stripped_hex = hex.strip("# ")

    # Validate Hex
    # https://stackoverflow.com/questions/30241375/python-how-to-check-if-string-is-a-hex-color-code
    match = search(r"^(?:[0-9a-fA-F]{3}){1,2}$", stripped_hex)
    if not match:
        return None

    # https://www.30secondsofcode.org/python/s/hex-to-rgb/
    return tuple(int(stripped_hex[i : i + 2], 16) for i in (0, 2, 4))
