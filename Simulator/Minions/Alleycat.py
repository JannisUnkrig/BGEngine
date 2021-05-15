from Simulator.Minion import Minion, Keyword, Tribe
from Simulator.Minions.Tokens.Tabbycat import Tabbycat


class Alleycat(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Alleycat"
        self.tier = 1
        self.attack = 1
        self.health = 1
        self.keywords = [Keyword.BATTLECRY]
        self.tribe = [Tribe.BEAST]

    def battlecry(self, player, future_pos, _):
        player.try_summon(Tabbycat(), future_pos, make_golden=self.golden, leave_one_free_space=True)
