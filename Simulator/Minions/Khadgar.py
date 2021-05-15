from Simulator.Minion import Minion


class Khadgar(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Khadgar"
        self.tier = 3
        self.attack = 2
        self.health = 2

        # actual implementation in class Combat and Player
