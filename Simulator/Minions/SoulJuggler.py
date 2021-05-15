import random

from Simulator.Minion import Minion, Tribe, TriggerCombat


class SoulJuggler(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Soul Juggler"
        self.tier = 3
        self.attack = 3
        self.health = 3
        self.triggerCombat = [TriggerCombat.ON_AND_AFTER_FRIENDLY_GETS_KILLED]

    def on_and_after_friendly_gets_killed(self, died):
        if not self.is_on_board() or Tribe.DEMON not in died.tribe:
            return
        self.combatant.combat.add_to_whenever_or_after_dies_trigger_list(self)

    def resolve_effect(self):
        n = self.double_if_golden(1)
        for _ in range(n):
            alive_enemies = list(filter(lambda m: (m.is_alive()) and (m.is_on_board()), self.combatant.enemy.board))
            if len(alive_enemies) > 0:
                self.combatant.deal_damage(3, self, random.choice(alive_enemies))

