from typing import Optional

from .player import Player


class MasterPlayer:
    def __init__(self) -> None:
        self.players: dict[int, Player] = {}

    def create_player(self, serverId: int) -> Player:
        self.players[serverId] = Player()
        return self.players[serverId]

    def get_player(self, serverId: int) -> Optional[Player]:
        return self.players.get(serverId)

    def destory_player(self, serverId: int) -> None:
        self.players.pop(serverId)
