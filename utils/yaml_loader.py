from typing import cast

from yaml import Loader, load


class YamlReadError(Exception):
    pass


def load_yaml() -> dict:
    configs = {}
    with open("./configs.yaml", "r", encoding="utf-8") as file:
        configs = load(file, Loader)

    if not len(configs):
        raise YamlReadError("No configs were loaded from configs.yaml!")

    return cast(dict, configs)
