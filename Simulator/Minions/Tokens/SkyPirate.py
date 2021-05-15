from Simulator.Minion import Minion, Tribe


class SkyPirate(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Sky Pirate"
        self.token = True
        self.attack = 1
        self.health = 1
        self.tribe = [Tribe.PIRATE]
