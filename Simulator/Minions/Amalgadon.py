from Simulator.Minion import Minion, Keyword, Tribe


class Amalgadon(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Amalgadon"
        self.tier = 6
        self.attack = 6
        self.health = 6
        self.keywords = [Keyword.BATTLECRY]
        self.tribe = [Tribe.BEAST, Tribe.DEMON, Tribe.DRAGON, Tribe.ELEMENTAL, Tribe.MECH, Tribe.MURLOC, Tribe.PIRATE]

    def battlecry(self, player, _, __):
        n = len(player.get_one_minion_from_each_tribe_on_board()) * self.double_if_golden(1)
        for _ in range(n):
            player.adapt_randomly(self)
