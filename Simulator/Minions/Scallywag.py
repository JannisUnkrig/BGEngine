from Simulator.Minion import Minion, Keyword, Tribe
from Simulator.Minions.Tokens.SkyPirate import SkyPirate


class Scallywag(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Scallywag"
        self.tier = 1
        self.attack = 2
        self.health = 1
        self.keywords = [Keyword.DEATHRATTLE]
        self.tribe = [Tribe.PIRATE]

    def deathrattle(self):
        tmp = self.combatant.try_summon_minions([SkyPirate()], 1, self, self.golden, ignore_khadgar=True)
        if len(tmp) == 0:
            return

        initial = tmp[0]
        iterations_left = self.combatant.get_khadgar_multiplier() - 1
        for _ in range(iterations_left):
            copy = self.combatant.try_summon_minions([initial], 1, initial, self.golden, ignore_khadgar=True)
            if len(copy) > 0:
                self.combatant.attack(copy[0])
        self.combatant.attack(initial)
