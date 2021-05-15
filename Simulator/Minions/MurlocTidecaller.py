from Simulator.Minion import Minion, Tribe, TriggerTavern, TriggerCombat


class MurlocTidecaller(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Murloc Tidecaller"
        self.tier = 1
        self.attack = 1
        self.health = 2
        self.triggerTavern = [TriggerTavern.ON_SUMMON]
        self.triggerCombat = [TriggerCombat.ON_FRIENDLY_SUMMON]
        self.tribe = [Tribe.MURLOC]

    def on_summon(self, player, summoned):
        if Tribe.MURLOC in summoned.tribe:
            player.buff(self, self.double_if_golden(1), 0)

    def on_friendly_summon(self, summoned):
        if Tribe.MURLOC in summoned.tribe:
            self.combatant.buff(self, self.double_if_golden(1), 0)
