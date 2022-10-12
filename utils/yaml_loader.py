from yaml import load, Loader
from typing import cast

class YamlReadError(Exception):
    pass

def load_yaml() -> dict:
    configs = {}
    with open("./configs.yaml", "r") as file:
        configs = load(file, Loader)

    if not len(configs):
        raise YamlReadError("No configs were loaded from configs.yaml!")

    return cast(dict, configs)