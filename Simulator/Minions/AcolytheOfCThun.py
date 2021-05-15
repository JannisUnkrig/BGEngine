from Simulator.Minion import Minion, Keyword


class AcolytheOfCThun(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Acolythe of C´Thun"
        self.tier = 1
        self.attack = 2
        self.health = 2
        self.keywords = [Keyword.TAUNT, Keyword.REBORN]
