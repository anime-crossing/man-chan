from .player import Player

class MasterPlayer:
    players: dict[int , Player] = {}

    @classmethod
    def create(cls):
        return cls()

    def createPlayer(self, serverId: int):
        self.players[serverId] = Player()

    def getPlayer(self, serverId: int):
        return  self.players.get(serverId)