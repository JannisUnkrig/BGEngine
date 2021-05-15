from Simulator.Minion import Minion, Tribe


class WaterDroplet(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Water Droplet"
        self.token = True
        self.attack = 2
        self.health = 2
        self.tribe = [Tribe.ELEMENTAL]
