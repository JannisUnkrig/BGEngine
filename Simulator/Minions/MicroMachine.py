from Simulator.Minion import Minion, Tribe, TriggerTavern


class MicroMachine(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Micro Machine"
        self.tier = 1
        self.attack = 1
        self.health = 2
        self.triggerTavern = [TriggerTavern.ON_START_OF_TURN]
        self.tribe = [Tribe.MECH]

    def on_start_of_turn(self, player):
        player.buff(self, self.double_if_golden(1), 0)
