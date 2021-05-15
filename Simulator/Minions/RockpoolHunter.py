from Simulator.Minion import Minion, Keyword, Tribe


class RockpoolHunter(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Rockpool Hunter"
        self.tier = 1
        self.attack = 2
        self.health = 3
        self.keywords = [Keyword.BATTLECRY]
        self.tribe = [Tribe.MURLOC]

    def battlecry(self, player, _, bc_target_idx):
        b = player.get_board()
        if len(b) == 0:
            return
        bc_target = b[bc_target_idx]
        murlocs = list(filter(lambda m: Tribe.MURLOC in m.tribe, b))
        if len(murlocs) > 0 and Tribe.MURLOC not in bc_target.tribe:
            player.validBcTarget = False
            return

        if Tribe.MURLOC in bc_target.tribe:
            player.buff(bc_target, self.double_if_golden(1), self.double_if_golden(1))
