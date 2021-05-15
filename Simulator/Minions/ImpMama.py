from Simulator.Minion import Minion, Tribe, TriggerCombat, Keyword


class ImpMama(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Imp Mama"
        self.tier = 6
        self.attack = 6
        self.health = 8
        self.triggerCombat = [TriggerCombat.ON_TAKE_DAMAGE]
        self.tribe = [Tribe.DEMON]

    def on_take_damage(self):
        if not self.is_on_board():
            return
        options = []
        options.extend(self.combatant.combat.game.minionPool.allDemons)
        options.extend(self.combatant.combat.game.minionPool.allAll)
        summoned = self.combatant.try_summon_minions(options, self.double_if_golden(1), self,
                                                     after_death_collection=False)
        for m in summoned:
            m.keywords.append(Keyword.TAUNT)

