import random

from Simulator.Minion import Minion, Tribe, TriggerTavern, Keyword


class MicroMummy(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Micro Mummy"
        self.tier = 1
        self.attack = 1
        self.health = 2
        self.keywords = [Keyword.REBORN]
        self.triggerTavern = [TriggerTavern.ON_END_OF_TURN]
        self.tribe = [Tribe.MECH]

    def on_end_of_turn(self, player):
        other_minions = list(filter(lambda m: m != self, player.get_board()))
        if len(other_minions) > 0:
            player.buff(random.choice(other_minions), self.double_if_golden(1), 0)
