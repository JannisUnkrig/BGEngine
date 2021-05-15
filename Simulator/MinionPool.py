import random

from Simulator.Minion import Minion, Keyword
from Simulator.Minions.Amalgadon import Amalgadon
from Simulator.Minions.BaronRivendare import BaronRivendare
from Simulator.Minions.BrannBronzebeard import BrannBronzebeard
from Simulator.Minions.DeckSwabbie import DeckSwabbie
from Simulator.Minions.DreadAdmiralEliza import DreadAdmiralEliza
from Simulator.Minions.ImpMama import ImpMama
from Simulator.Minions.Khadgar import Khadgar
from Simulator.Minions.MicroMachine import MicroMachine
from Simulator.Minions.MicroMummy import MicroMummy
from Simulator.Minions.MurlocTidecaller import MurlocTidecaller
from Simulator.Minions.MurlocTidehunter import MurlocTidehunter
from Simulator.Minions.NathrezimOverseer import NathrezimOverseer
from Simulator.Minions.RedWhelp import RedWhelp
from Simulator.Minions.RefreshingAnomaly import RefreshingAnomaly
from Simulator.Minions.RockpoolHunter import RockpoolHunter
from Simulator.Minions.Scallywag import Scallywag
from Simulator.Minions.Sellemental import Sellemental
from Simulator.Minions.Siegebreaker import Siegebreaker
from Simulator.Minions.SoulJuggler import SoulJuggler
from Simulator.Minions.Tokens.Microbot import Microbot
from Simulator.Minions.Tokens.MurlocScout import MurlocScout
from Simulator.Minions.Tokens.Plant import Plant
from Simulator.Minions.Tokens.SkyPirate import SkyPirate
from Simulator.Minions.Tokens.Tabbycat import Tabbycat
from Simulator.Minions.Tokens.Voidwalker import Voidwalker
from Simulator.Minions.Tokens.WaterDroplet import WaterDroplet
from Simulator.Minions.UnstableGhoul import UnstableGhoul
from Simulator.Minions.AcolytheOfCThun import AcolytheOfCThun
from Simulator.Minions.DragonspawnLieutenant import DragonspawnLieutenant
from Simulator.Minions.Voidlord import Voidlord
from Simulator.Minions.WrathWeaver import WrathWeaver
from Simulator.Minions.VulgarHomunculus import VulgarHomunculus
from Simulator.Minions.FiendishServant import FiendishServant
from Simulator.Minions.ScavengingHyena import ScavengingHyena
from Simulator.Minions.Alleycat import Alleycat


class MinionPool:

    def __init__(self):
        self.dummy = Minion()
        self.allBeasts = [Alleycat, ScavengingHyena]
        self.allBeastSupports = []
        self.allDemons = [FiendishServant, VulgarHomunculus, NathrezimOverseer, Siegebreaker, Voidlord, ImpMama]
        self.allDemonSupports = [WrathWeaver, SoulJuggler]
        self.allDragons = [DragonspawnLieutenant, RedWhelp]
        self.allDragonSupports = []
        self.allElementals = [RefreshingAnomaly, Sellemental]
        self.allElementalSupports = []
        self.allMechs = [MicroMachine, MicroMummy]
        self.allMechSupports = []
        self.allMurlocs = [MurlocTidecaller, MurlocTidehunter, RockpoolHunter]
        self.allMurlocSupports = []
        self.allPirates = [DeckSwabbie, Scallywag, DreadAdmiralEliza]
        self.allPirateSupports = []
        self.allNeutrals = [AcolytheOfCThun, UnstableGhoul, Khadgar, BrannBronzebeard, BaronRivendare]
        self.allAll = [Amalgadon]
        self.allTokens = [Microbot, MurlocScout, Plant, SkyPirate, Tabbycat, Voidwalker, WaterDroplet]

        self.allMinions = []  # doesn't include tokens TODO only five tribes per game
        self.allMinions.extend(self.allBeasts)
        self.allMinions.extend(self.allBeastSupports)
        self.allMinions.extend(self.allDemons)
        self.allMinions.extend(self.allDemonSupports)
        self.allMinions.extend(self.allDragons)
        self.allMinions.extend(self.allDragonSupports)
        self.allMinions.extend(self.allElementals)
        self.allMinions.extend(self.allElementalSupports)
        self.allMinions.extend(self.allMechs)
        self.allMinions.extend(self.allMechSupports)
        self.allMinions.extend(self.allMurlocs)
        self.allMinions.extend(self.allMurlocSupports)
        self.allMinions.extend(self.allPirates)
        self.allMinions.extend(self.allPirateSupports)
        self.allMinions.extend(self.allNeutrals)
        self.allMinions.extend(self.allAll)

        self.pool = []
        for minion_class in self.allMinions:
            if minion_class().tier == 1:
                count = 16
            elif minion_class().tier == 2:
                count = 15
            elif minion_class().tier == 3:
                count = 13
            elif minion_class().tier == 4:
                count = 11
            elif minion_class().tier == 5:
                count = 9
            else:
                count = 7

            for i in range(count):
                minion = minion_class()
                minion.isFromPool = True
                minion.id = self.allMinions.index(minion_class) + 1
                self.pool.append(minion)

    def get_minions(self, tavern_tier, how_many):
        result = []
        for _ in range(how_many):
            minions_of_tier = list(filter(lambda m: m.tier <= tavern_tier, self.pool))
            m2 = random.choice(minions_of_tier)
            result.append(m2)
            self.pool.remove(m2)
        return result

    def get_minions_specific_tier(self, tavern_tier, how_many):
        result = []
        for _ in range(how_many):
            minions_of_tier = list(filter(lambda m: m.tier == tavern_tier, self.pool))
            m2 = random.choice(minions_of_tier)
            result.append(m2)
            self.pool.remove(m2)
        return result

    def return_one(self, minion):
        if (not minion.token) and minion.isFromPool:
            m = type(minion)()
            m.isFromPool = True
            self.pool.append(m)

    def return_many(self, minions):
        for minion in minions:
            if (not minion.token) and minion.isFromPool:
                m = type(minion)()
                m.isFromPool = True
                self.pool.append(m)

    def __str__(self):
        d = dict()
        for m in self.pool:
            if m.name in d:
                d[m.name] += 1
            else:
                d[m.name] = 1
        s = str(d)
        s = s.replace(", ", "\n   ")
        s = s.replace("'", "")
        s = "Minion-Pool:\n\n   " + s[1:len(s) - 1]
        return s


def minion_from_string(minion_string):
    s = minion_string[0].upper() + minion_string[1:]
    try:
        minion_class = globals()[s]
        m = minion_class()
        return m
    except KeyError:
        return None


# eg: "4/2 golden fiendishServant (taunt, divineShield)" or just "fiendishServant"
def minion_from_advanced_string(minion_string):
    minion_string = minion_string.replace(", ", ",")
    parts = minion_string.split(" ")
    attack = None
    health = None
    golden = False
    minion = None
    keywords = []
    try:
        for part in parts:
            if part[0].isnumeric():
                a_h = part.split("/")
                attack = int(a_h[0])
                health = int(a_h[1])
            elif part == "golden":
                golden = True
            elif part[0] == "(":
                part = part[1:len(part) - 1]
                ks = part.split(",")
                for k in ks:
                    keywords.append(Keyword[k.upper()])
            else:
                minion = minion_from_string(part)
    except Exception:
        return None

    if minion is None:
        return None

    if attack is not None and health is not None:
        minion.attack = attack
        minion.health = health
    minion.golden = golden
    if len(keywords) > 0:
        minion.keywords = keywords

    return minion
