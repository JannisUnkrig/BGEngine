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
    DIVINESHIELD = 'Divine Shield'
    WINDFURY = 'Windfury'
    MEGAWINDFURY = 'Mega-Windfury'
    POISONOUS = 'Poisonous'
    REBORN = 'Reborn'
    MAGNETIC = 'Magnetic'
    FRENZY = 'Frenzy'
    FROZEN = 'Frozen'
    MENACE = 'Menace'
    GOLDENMENACE = 'Golden Menace'
    MODULE = 'Module'
    GOLDENMODULE = 'Golden Module'
    PLANTS = 'Plants'

    def __str__(self):
        return '%s' % self.value


class TriggerTavern(Enum):
    ON_OR_AFTER_PLAY = 2
    ON_SUMMON = 3
    ON_BUY = 4
    ON_SELL = 5
    ON_START_OF_TURN = 6
    ON_END_OF_TURN = 7
    ON_TAKE_HERO_DAMAGE = 8


class TriggerCombat(Enum):
    ON_ATTACK = 0
    ON_FRIENDLY_ATTACK = 1
    AFTER_ATTACK = 2  # but before death
    ON_FRIENDLY_GET_ATTACKED = 3
    AFTER_SURVIVE_ATTACK = 4
    ON_FRIENDLY_KILLS = 5
    ON_AND_AFTER_FRIENDLY_GETS_KILLED = 6
    ON_START_OF_COMBAT = 8
    ON_TAKE_DAMAGE = 9
    AFTER_FRIENDLY_LOSE_DIVINE_SHIELD = 10
    ON_FRIENDLY_SUMMON = 11
    AFTER_FRIENDLY_SUMMON = 12


class Minion:

    def __init__(self):
        self.name = "Dummy Minion"
        self.id = 0
        self.token = False
        self.tier = 1
        self.attack = 1
        self.health = 1
        self.keywords = []
        self.tribe = []
        self.golden = False
        self.triggerTavern = []
        self.triggerCombat = []
        self.isFromPool = False

        # only during combat
        self.combatant = None
        self.isUpcomingAttacker = False
        self.damageTaken = 0
        self.realTwin = None
        self.minionToRightBeforeDeath = None

    def is_alive(self):
        if self.health > 0:
            return True
        return False

    def is_dead(self):
        if self.health <= 0:
            return True
        return False

    def is_on_board(self):
        if self.combatant is None:
            return False
        return self not in self.combatant.combat.minions_removed_from_board

    def is_valid_attacker(self):
        return self.attack > 0 and self.is_alive() and self.is_on_board()

    def double_if_golden(self, num):
        if self.golden:
            return num * 2
        return num

    def get_copy(self):
        c = type(self)()
        c.attack = self.attack
        c.health = self.health
        c.keywords = self.keywords.copy()
        c.golden = self.golden
        c.isFromPool = False

        c.combatant = self.combatant
        c.damageTaken = self.damageTaken
        return c

    def __str__(self):
        if self.health != -100000:
            h = str(self.health)
        else:
            h = "x"
        s = str(self.attack) + "/" + h + " "
        if self.golden:
            s += "golden "
        s += self.name
        if len(self.keywords) > 0:
            s += " (" + ", ".join(str(k) for k in self.keywords) + ")"
        return s
