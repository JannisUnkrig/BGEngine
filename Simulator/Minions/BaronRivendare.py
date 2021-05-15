from Simulator.Minion import Minion


class BaronRivendare(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Baron Rivendare"
        self.tier = 5
        self.attack = 1
        self.health = 7

    # actual implementation in class Combat
