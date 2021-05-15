from Simulator.Minion import Minion, Keyword, Tribe


class Siegebreaker(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Siegebreaker"
        self.tier = 4
        self.attack = 5
        self.health = 8
        self.keywords = [Keyword.TAUNT]
        self.tribe = [Tribe.DEMON]

    # TODO Aura
