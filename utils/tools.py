from re import search
from typing import Any, Dict, List, Optional, Tuple


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


def dig(
    collection: Dict[Any, Any] | List[Any], *args: str | int
) -> Optional[Dict[Any, Any] | List[Any] | Any]:
    if collection is None:
        return None

    navigation = collection
    for index in args:
        if isinstance(navigation, dict):
            navigation = navigation.get(index, None)
        elif isinstance(navigation, list) and isinstance(index, int):
            try:
                navigation = navigation[index]  # type: ignore - is list
            except IndexError:
                navigation = None
        else:
            raise ValueError(f"Invalid type to index: {navigation} using [{index}]")

        if navigation is None:
            return None

    return navigation


def empty_or_default(value: Optional[Any], default: Optional[Any] = None) -> Any:
    if value is None or (hasattr(value, "__len__") and len(value) < 1):
        return None
    return value
