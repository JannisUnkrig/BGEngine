from Simulator.Minion import Minion, Keyword


class UnstableGhoul(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Unstable Ghoul"
        self.tier = 2
        self.attack = 1
        self.health = 3
        self.keywords = [Keyword.TAUNT, Keyword.DEATHRATTLE]

    def deathrattle(self):
        for _ in range(self.double_if_golden(1)):
            amob = self.combatant.combat.all_minions_on_board()
            filtered = list(filter(lambda m2: m2.is_on_board(), amob))
            for m in filtered:
                self.combatant.deal_damage(1, self, m)
