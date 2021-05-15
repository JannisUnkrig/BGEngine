from Simulator.Minion import Minion


class BrannBronzebeard(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Brann Bronzebeard"
        self.tier = 5
        self.attack = 2
        self.health = 4

    # actual implementation in class Player
