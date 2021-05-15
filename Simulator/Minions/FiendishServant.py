import random

from Simulator.Minion import Minion, Keyword, Tribe


class FiendishServant(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Fiendish Servant"
        self.tier = 1
        self.attack = 2
        self.health = 1
        self.keywords = [Keyword.DEATHRATTLE]
        self.tribe = [Tribe.DEMON]
        self.triggerCombat = []

    def deathrattle(self):
        alive_friends = list(filter(lambda m: (m.is_alive() and m.is_on_board()), self.combatant.board))
        if len(alive_friends) > 0:
            for _ in range(self.double_if_golden(1)):
                self.combatant.buff(random.choice(alive_friends), self.attack, 0)
