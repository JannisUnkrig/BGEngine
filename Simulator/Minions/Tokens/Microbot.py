from Simulator.Minion import Minion, Tribe


class Microbot(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Microbot"
        self.token = True
        self.attack = 1
        self.health = 1
        self.tribe = [Tribe.MECH]
