

class Spell:

    def __init__(self):
        self.name = "Dummy Spell"
        self.cost = 0

    def cast(self, player, target_idx):
        pass

    def __str__(self):
        return str(self.cost) + " Gold " + self.name
