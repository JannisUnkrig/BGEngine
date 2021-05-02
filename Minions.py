import random
from enum import Enum


class Tribe(Enum):
    BEAST = 1
    DEMON = 2
    DRAGON = 3
    ELEMENTAL = 4
    MECH = 5
    MURLOC = 6
    PIRATE = 7


class Keyword(Enum):
    BATTLECRY = 'Battlecry'
    DEATHRATTLE = 'Deathrattle'
    OVERKILL = 'Overkill'
    TAUNT = 'Taunt'
    DIVINE_SHIELD = 'Divine Shield'
    WINDFURY = 'Windfury'
    MEGAWINDFURY = 'Mega-Windfury'
    POISONOUS = 'Poisonous'
    REBORN = 'Reborn'
    MAGNETIC = 'Magnetic'
    FRENZY = 'Frenzy'
    FROZEN = 'Frozen'
    MENACE = 'Menace'
    MODULE = 'Module'
    PLANTS = 'Plants'

    def __str__(self):
        return '%s' % self.value


class TriggerTavern(Enum):
    ON_PLAY = 1
    AFTER_PLAY = 2
    ON_SUMMON = 3
    AFTER_BUY = 4
    ON_SELL = 5
    ON_START_OF_TURN = 6
    ON_END_OF_TURN = 7
    ON_TAKE_HERO_DAMAGE = 8


class TriggerCombat(Enum):
    ON_ATTACK = 1
    AFTER_ATTACK = 2  # but before death
    ON_GET_ATTACKED = 3
    AFTER_SURVIVE_ATTACK = 4
    ON_KILL = 5
    ON_GET_KILLED = 6
    AFTER_GET_KILLED = 7
    ON_START_OF_COMBAT = 8
    ON_TAKE_DAMAGE = 9
    AFTER_LOSE_DIVINE_SHIELD = 10
    ON_SUMMON = 11
    AFTER_SUMMON = 12


# ############################# Actual Minions ############################# #

class Minion:

    def __init__(self):
        self.name = "Dummy Minion"
        self.token = False
        self.tier = 1
        self.attack = 1
        self.health = 1
        self.keywords = []
        self.tribe = []
        self.triggerTavern = []
        self.triggerCombat = []
        self.killedBy = None  # only for combat

    def __str__(self):
        s = str(self.attack) + "/" + str(self.health) + " " + self.name
        if len(self.keywords) > 0:
            s += " (" + ", ".join(str(k) for k in self.keywords) + ")"
        return s


class Alleycat(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Alleycat"
        self.tier = 1
        self.attack = 1
        self.health = 1
        self.keywords = [Keyword.BATTLECRY]
        self.tribe = [Tribe.BEAST]

    def battlecry(self, player, position, _):
        if player.get_board_size() <= 5:
            player.summon([self], Tabbycat(), position)


class Tabbycat(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Tabbycat"
        self.token = True
        self.attack = 1
        self.health = 1
        self.tribe = [Tribe.BEAST]


class ScavengingHyena(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Scavenging Hyena"
        self.tier = 1
        self.attack = 2
        self.health = 2
        self.tribe = [Tribe.BEAST]
        self.triggerCombat = [TriggerCombat.ON_GET_KILLED]

    def on_get_killed(self, killed):  # TODO
        if killed.tribe is Tribe.BEAST and killed is not self:
            self.attack += 2
            self.health += 1


class FiendishServant(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Fiendish Servant"
        self.tier = 1
        self.attack = 2
        self.health = 1
        self.keywords = [Keyword.DEATHRATTLE]
        self.tribe = [Tribe.DEMON]
        self.triggerCombat = [TriggerCombat.AFTER_GET_KILLED]

    def deathrattle(self, arena, pos, own_board, enemy_board):
        alive = list(filter(lambda m: m.health > 0, own_board))  # could cause trouble with other queued deathrattles
        if len(alive) > 0:
            arena.enqueue(arena.buff, random.choice(alive), self.attack, 0)


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
        player.take_hero_damage(2)


class WrathWeaver(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Wrath Weaver"
        self.tier = 1
        self.attack = 1
        self.health = 3
        self.triggerTavern = [TriggerTavern.AFTER_PLAY]

    def after_play(self, player, minion):
        if minion.tribe is Tribe.DEMON:
            player.take_hero_damage(1)
            self.attack += 2
            self.attack += 2


class DragonspawnLieutenant(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Dragonspawn Lieutenant"
        self.tier = 1
        self.attack = 2
        self.health = 3
        self.keywords = [Keyword.TAUNT]
        self.tribe = [Tribe.DRAGON]


class AcolytheOfCThun(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Acolythe of C'Thun"
        self.tier = 1
        self.attack = 2
        self.health = 2
        self.keywords = [Keyword.TAUNT, Keyword.REBORN]


class UnstableGhoul(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Unstable Ghoul"
        self.tier = 2
        self.attack = 1
        self.health = 3
        self.keywords = [Keyword.TAUNT, Keyword.DEATHRATTLE]

    def deathrattle(self, arena, pos, own_board, enemy_board):
        for m in enemy_board:
            arena.enqueue(arena.take_damage, 1, m, self)
        for m in own_board:
            if m != self:
                arena.enqueue(arena.take_damage, 1, m, self)


class Scallywag(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Scallywag"
        self.tier = 1
        self.attack = 2
        self.health = 1
        self.keywords = [Keyword.BATTLECRY]
        self.tribe = [Tribe.PIRATE]

    def deathrattle(self, arena, pos, own_board, enemy_board):
        arena.enqueue(arena.summon, [self], SkyPirate(), own_board, pos)


class SkyPirate(Minion):

    def __init__(self):
        super().__init__()
        self.name = "Sky Pirate"
        self.token = True
        self.attack = 1
        self.health = 1
        self.triggerCombat = [TriggerCombat.AFTER_SUMMON]
        self.tribe = [Tribe.PIRATE]

    def after_summon(self, arena, summoners, summoned, own_board, position, opponents_board):
        if summoned == self:
            arena.attack(self, opponents_board)  # no enqueue because it attacks instantly


# ############################# Minion Pool ############################# #

class Pool:
    allBeasts = [Alleycat(), ScavengingHyena()]
    allDemons = [FiendishServant(), VulgarHomunculus(), WrathWeaver()]
    allDragons = [DragonspawnLieutenant()]
    allElementals = []
    allMechs = []
    allMurlocs = []
    allPirates = []
    allNeutrals = [AcolytheOfCThun(), UnstableGhoul()]

    allMinions = allBeasts + allDemons + allDragons + allElementals + allMechs + allMurlocs + allPirates + allNeutrals

    pool = []
    for minion in allMinions:
        if minion.tier == 1:
            count = 16
        elif minion.tier == 2:
            count = 15
        elif minion.tier == 3:
            count = 13
        elif minion.tier == 4:
            count = 11
        elif minion.tier == 5:
            count = 9
        else:
            count = 7

        for i in range(count):
            pool.append(type(minion)())


def get_from_pool(tavern_tier, how_many):
    i = 0
    result = []
    while i < how_many:
        m = random.choice(Pool.pool)
        if m.tier <= tavern_tier:
            result.append(m)
            Pool.pool.remove(m)
            i += 1
    return result


def return_one_to_pool(minion):
    if not minion.token:
        Pool.pool.append(type(minion)())


def return_many_to_pool(minions):
    for minion in minions:
        if not minion.token:
            Pool.pool.append(type(minion)())


def pool_as_string():
    d = dict()
    for m in Pool.pool:
        if m.name in d:
            d[m.name] += 1
        else:
            d[m.name] = 1
    return str(d)
