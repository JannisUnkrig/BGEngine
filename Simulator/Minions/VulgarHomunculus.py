from Simulator.Minion import Minion, Keyword, Tribe


class VulgarHomunculus(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Vulgar Homunculus"
        self.tier = 1
        self.attack = 2
        self.health = 4
        self.keywords = [Keyword.BATTLECRY, Keyword.TAUNT]
        self.tribe = [Tribe.DEMON]

    def battlecry(self, player, _, __):
        player.take_hero_damage_on_own_turn(2)
