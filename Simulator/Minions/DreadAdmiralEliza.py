from Simulator.Minion import Minion, Tribe, TriggerCombat


class DreadAdmiralEliza(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Dread Admiral Eliza"
        self.tier = 6
        self.attack = 6
        self.health = 7
        self.tribe = [Tribe.PIRATE]
        self.triggerCombat = [TriggerCombat.ON_FRIENDLY_ATTACK]

    def on_friendly_attack(self, attacker):
        if Tribe.PIRATE in attacker.tribe:
            alive_friends = list(filter(lambda m: (m.is_alive() and m.is_on_board()), self.combatant.board))
            for minion in alive_friends:
                self.combatant.buff(minion, self.double_if_golden(2), self.double_if_golden(1))
