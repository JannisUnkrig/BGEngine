import random

from Simulator.Minion import Minion, Tribe, TriggerCombat


class RedWhelp(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Red Whelp"
        self.tier = 1
        self.attack = 1
        self.health = 2
        self.triggerCombat = [TriggerCombat.ON_START_OF_COMBAT]
        self.tribe = [Tribe.DRAGON]

        self.initialDragonCount = 0

    def setup_on_start_of_combat(self):
        for m in self.combatant.board:
            if Tribe.DRAGON in m.tribe:
                self.initialDragonCount += 1

    def on_start_of_combat(self):
        n = self.double_if_golden(1)
        for _ in range(n):
            if self.is_dead():
                return
            alive_enemies = list(filter(lambda m: m.is_alive(), self.combatant.enemy.board))
            if len(alive_enemies) > 0:
                self.combatant.deal_damage(self.initialDragonCount, self, random.choice(alive_enemies))
