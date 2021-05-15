from Simulator.Minion import Minion, Keyword, Tribe


class DeckSwabbie(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Deck Swabbie"
        self.tier = 1
        self.attack = 2
        self.health = 2
        self.keywords = [Keyword.BATTLECRY]
        self.tribe = [Tribe.PIRATE]

    def battlecry(self, player, _, __):
        player.tavern.tierUpCost -= self.double_if_golden(1)
        if player.tavern.tierUpCost < 0:
            player.tavern.tierUpCost = 0

