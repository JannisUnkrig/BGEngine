from Simulator.Minion import Minion, Keyword, Tribe
from Simulator.Minions.Tokens.MurlocScout import MurlocScout


class MurlocTidehunter(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Murloc Tidehunter"
        self.tier = 1
        self.attack = 2
        self.health = 1
        self.keywords = [Keyword.BATTLECRY]
        self.tribe = [Tribe.MURLOC]

    def battlecry(self, player, future_pos, _):
        player.try_summon(MurlocScout(), future_pos, make_golden=self.golden, leave_one_free_space=True)
