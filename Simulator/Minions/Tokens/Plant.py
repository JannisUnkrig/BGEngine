from Simulator.Minion import Minion


class Plant(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Plant"
        self.token = True
        self.attack = 1
        self.health = 1
