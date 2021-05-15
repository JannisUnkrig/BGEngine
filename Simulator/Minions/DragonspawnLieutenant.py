from Simulator.Minion import Minion, Keyword, Tribe


class DragonspawnLieutenant(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Dragonspawn Lieutenant"
        self.tier = 1
        self.attack = 2
        self.health = 3
        self.keywords = [Keyword.TAUNT]
        self.tribe = [Tribe.DRAGON]
