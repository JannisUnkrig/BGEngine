from Simulator.Minion import Minion, Tribe, TriggerTavern
from Simulator.Minions.Tokens.WaterDroplet import WaterDroplet


class Sellemental(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Sellemental"
        self.tier = 1
        self.attack = 2
        self.health = 2
        self.triggerTavern = [TriggerTavern.ON_SELL]
        self.tribe = [Tribe.ELEMENTAL]

    def on_sell(self, player):
        for _ in range(self.double_if_golden(1)):
            player.try_add_to_hand(WaterDroplet())
