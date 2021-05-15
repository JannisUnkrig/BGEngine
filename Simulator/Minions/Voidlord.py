from Simulator.Minion import Minion, Keyword, Tribe
from Simulator.Minions.Tokens.Voidwalker import Voidwalker


class Voidlord(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Voidlord"
        self.tier = 5
        self.attack = 3
        self.health = 9
        self.keywords = [Keyword.DEATHRATTLE, Keyword.TAUNT]
        self.tribe = [Tribe.DEMON]

    def deathrattle(self):
        self.combatant.try_summon_minions([Voidwalker()], 3, self, make_golden=self.golden)
