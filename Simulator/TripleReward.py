from Simulator.Spell import Spell


class TripleReward(Spell):

    def __init__(self, tier):
        super().__init__()
        self.name = "Triple Reward"
        tier += 1
        if tier > 6:
            tier = 6
        self.discover_from_tier = tier

    def cast(self, player, target_idx):
        player.discover_options = player.game.minionPool.get_minions_specific_tier(self.discover_from_tier, 3)
        player.hand.remove(self)

    def __str__(self):
        s = super().__str__()
        s += " (Discover Tier: " + str(self.discover_from_tier) + ")"
        return s
