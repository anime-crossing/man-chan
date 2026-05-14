import os
from typing import Any, cast

from .config_mapper import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


class EnvLoader:

    def __init__(self):
        self._vars = dict()

        with open(".env", "r", encoding="utf-8") as file:
            for line in file.readlines():
                if len(line.strip()) < 1 or line.startswith("#"):
                    continue

                key, val = line.split("=")
                self._vars[key.strip()] = val.strip()

    def get_db(self):
        return self._vars.get(POSTGRES_DB)

    def get_host(self):
        return self._vars.get(POSTGRES_HOST)

    def get_pass(self):
        return self._vars.get(POSTGRES_PASSWORD)

    def get_user(self):
        return self._vars.get(POSTGRES_USER)

    def get_port(self):
        return self._vars.get(POSTGRES_PORT)

    def validate_db(self) -> bool:
        return (
            len(self.get_db())
            + len(self.get_host())
            + len(self.get_pass())
            + len(self.get_user())
        ) > 0

    def db_url(self) -> str:
        return f"postgresql+psycopg2://{self.get_user()}:{self.get_pass()}@{self.get_host()}:{self.get_port()}/"
