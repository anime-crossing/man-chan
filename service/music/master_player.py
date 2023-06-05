from .player import Player

class MasterPlayer:
    
    def __init__(self) -> None:
        self.players: dict[int , Player] = {}

    def createPlayer(self, serverId: int):
        self.players[serverId] = Player()

    def getPlayer(self, serverId: int):
        return  self.players.get(serverId)