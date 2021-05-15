from Simulator.Minion import Minion, TriggerTavern, Tribe


class WrathWeaver(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Wrath Weaver"
        self.tier = 1
        self.attack = 1
        self.health = 3
        self.triggerTavern = [TriggerTavern.ON_OR_AFTER_PLAY]

    def on_or_after_play(self, player, minion):
        if Tribe.DEMON in minion.tribe:
            player.take_hero_damage_on_own_turn(1)
            player.buff(self, self.double_if_golden(2), self.double_if_golden(2))
