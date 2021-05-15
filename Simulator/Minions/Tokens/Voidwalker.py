from Simulator.Minion import Minion, Keyword, Tribe


class Voidwalker(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Voidwalker"
        self.token = True
        self.tier = 1
        self.attack = 1
        self.health = 3
        self.keywords = [Keyword.TAUNT]
        self.tribe = [Tribe.DEMON]

    def deathrattle(self):
        self.combatant.try_summon_minions([Voidwalker()], 3, self, make_golden=self.golden)
