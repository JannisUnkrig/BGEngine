from Simulator.Minion import Minion, Keyword, Tribe


class NathrezimOverseer(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Nathrezim Overseer"
        self.tier = 2
        self.attack = 2
        self.health = 3
        self.keywords = [Keyword.BATTLECRY]
        self.tribe = [Tribe.DEMON]

    def battlecry(self, player, _, bc_target_idx):
        b = player.get_board()
        if len(b) == 0:
            return
        bc_target = b[bc_target_idx]
        demons = list(filter(lambda m: Tribe.DEMON in m.tribe, b))
        if len(demons) > 0 and Tribe.DEMON not in bc_target.tribe:
            player.validBcTarget = False
            return

        if Tribe.DEMON in bc_target.tribe:
            player.buff(bc_target, self.double_if_golden(2), self.double_if_golden(2))
