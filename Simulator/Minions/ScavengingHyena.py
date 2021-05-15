from Simulator.Minion import Minion, Tribe, TriggerCombat


class ScavengingHyena(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Scavenging Hyena"
        self.tier = 1
        self.attack = 2
        self.health = 2
        self.tribe = [Tribe.BEAST]
        self.triggerCombat = [TriggerCombat.ON_AND_AFTER_FRIENDLY_GETS_KILLED]

    def on_and_after_friendly_gets_killed(self, killed):
        if Tribe.BEAST in killed.tribe:
            self.combatant.combat.add_to_whenever_or_after_dies_trigger_list(self)

    def resolve_effect(self):
        self.combatant.buff(self, self.double_if_golden(2), self.double_if_golden(1))
