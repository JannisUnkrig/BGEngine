from Simulator.Minion import Minion, Keyword, Tribe


class RefreshingAnomaly(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Refreshing Anomaly"
        self.tier = 1
        self.attack = 1
        self.health = 3
        self.keywords = [Keyword.BATTLECRY]
        self.tribe = [Tribe.ELEMENTAL]

    def battlecry(self, player, _, __):
        if player.tavern.freeRolls < self.double_if_golden(1):
            player.tavern.freeRolls = self.double_if_golden(1)
