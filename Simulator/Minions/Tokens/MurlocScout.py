from Simulator.Minion import Minion, Tribe


class MurlocScout(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Murloc Scout"
        self.token = True
        self.attack = 1
        self.health = 1
        self.tribe = [Tribe.MURLOC]
