import random

from Simulator.Minion import Keyword, TriggerCombat
from Simulator.Minions.BaronRivendare import BaronRivendare
from Simulator.Minions.Khadgar import Khadgar
from Simulator.Minions.Tokens.Microbot import Microbot
from Simulator.Minions.Tokens.Plant import Plant


class Combatant:

    def __init__(self, player, enemy, combat):
        # game logic
        self.player = player
        self.board = player.get_combat_board()
        for m in self.board:
            m.combatant = self
            if TriggerCombat.ON_START_OF_COMBAT in m.triggerCombat:
                m.setup_on_start_of_combat()
        if len(self.board) > 0:
            self.board[0].isUpcomingAttacker = True
        self.enemy = enemy
        self.graveyard = []

        # technical stuff
        self.combat = combat
        self.deathrattleDepth = 0
        self.previousAttacker = None
        self.start_of_combat_effect_minions = list(
            filter(lambda m2: TriggerCombat.ON_START_OF_COMBAT in m2.triggerCombat, self.board))

    def activate_next_start_of_combat_effect(self):
        self.start_of_combat_effect_minions = list(
            filter(lambda m2: m2.is_alive(), self.start_of_combat_effect_minions))
        if len(self.start_of_combat_effect_minions) == 0:
            return
        m = self.start_of_combat_effect_minions.pop(0)
        self.log(str(m) + " triggers its 'start of combat' effect.")
        m.on_start_of_combat()
        self.combat.clean_up()

    def attack(self, attacking_minion=None):
        if attacking_minion is None:
            attacker = self.find_upcoming_attacker()
            if attacker == self.previousAttacker:
                self.pass_upcoming_attacker(attacker)
                attacker = self.find_upcoming_attacker()
            self.previousAttacker = attacker
        else:
            attacker = attacking_minion

        no_attacks = 1
        if Keyword.WINDFURY in attacker.keywords:
            no_attacks = 2
        if Keyword.MEGAWINDFURY in attacker.keywords:
            no_attacks = 4
        for i in range(no_attacks):
            if not attacker.is_alive():
                break
            if len(list(filter(lambda m2: m2.is_alive(), self.enemy.board))) == 0:
                break
            target = self.get_attack_target()

            self.log(str(attacker) + " attacks " + str(target) + ".")
            if TriggerCombat.ON_ATTACK in attacker.triggerCombat:
                self.log(str(attacker) + " triggered its 'whenever this attacks' effect.")
                attacker.on_attack()  # Glyph Guardian
            for m in self.board:
                if TriggerCombat.ON_FRIENDLY_ATTACK in m.triggerCombat:
                    self.log(str(m) + " triggered its 'whenever a friendly minion attacks' effect.")
                    m.on_friendly_attack(attacker)  # Ripsnarl, Eliza

            self.deal_damage(attacker.attack, attacker, target)
            self.take_damage(target.attack, attacker, target)

            if TriggerCombat.AFTER_ATTACK in attacker.triggerCombat:
                self.log(str(attacker) + " triggered its 'after attack' effect.")
                attacker.after_attack()
            if TriggerCombat.AFTER_SURVIVE_ATTACK in target.triggerCombat and target.is_alive():
                attacker.after_survive_attack()

            self.deathrattleDepth += 1
            self.combat.clean_up()
            self.deathrattleDepth -= 1

            if self.deathrattleDepth == 0:
                self.combat.resolve_extra_attack_list()

    def find_upcoming_attacker(self):
        for minion in self.board:
            if minion.isUpcomingAttacker:
                return minion
        return self.board[0]  # no minion with is_upcoming_attacker will exist if all minions die simultaneously

    # takes the current upcomingAttacker
    def pass_upcoming_attacker(self, minion):
        minion.isUpcomingAttacker = False
        old_idx = self.board.index(minion)
        for i in range(len(self.board)):
            idx = (old_idx + 1 + i) % len(self.board)
            if self.board[idx].is_valid_attacker():
                self.board[idx].isUpcomingAttacker = True
                return

    def get_attack_target(self):
        taunts = []
        for m in self.enemy.board:
            if (Keyword.TAUNT in m.keywords) and m.is_alive():
                taunts.append(m)
        if len(taunts) == 0:
            return random.choice(list(filter(lambda m2: m2.is_alive(), self.enemy.board)))
        else:
            return random.choice(taunts)

    def deal_damage(self, how_much, who, to):
        self.take_damage(how_much, to, who)

        if Keyword.OVERKILL in who.keywords and to.health < 0:
            self.log(str(who) + " triggers its overkill effect.")
            who.overkill(self.enemy.board, self.board)

    def take_damage(self, how_much, who, by):
        if how_much <= 0:
            return
        who_was_living = who.is_alive()

        # handle divine shield
        if Keyword.DIVINESHIELD in who.keywords:
            who.keywords.remove(Keyword.DIVINESHIELD)
            self.log(str(who) + " lost his divine shield.")
            for m in self.board:
                if TriggerCombat.AFTER_FRIENDLY_LOSE_DIVINE_SHIELD in m.triggerCombat:
                    self.log(str(m) + " triggers its 'after a friendly minion loses divine shield' effect.")
                    m.after_lose_divine_shield()
            return

        # deal damage
        who.health -= how_much
        self.log(str(who) + " took " + str(how_much) + " damage.")

        if TriggerCombat.ON_TAKE_DAMAGE in who.triggerCombat:
            self.log(str(who) + " triggers its 'whenever this minion takes damage' effect.")
            who.on_take_damage()

        if who.damageTaken == 0:
            if Keyword.FRENZY in who.keywords and who.health > 0:
                who.frenzy()
        who.damageTaken += how_much

        # poison
        if Keyword.POISONOUS in by.keywords:
            who.health = -10000
            self.log(str(who) + " was poisoned.")

        if who_was_living and who.is_dead():
            for m in self.board:
                if TriggerCombat.ON_FRIENDLY_KILLS in m.triggerCombat:
                    m.on_friendly_kills(by)

    def buff(self, minion, attack, health):
        minion.attack += attack
        minion.health += health
        self.log("Buffed " + str(minion) + " with (" + str(attack) + "/" + str(health) + ").")

    # summons copys of minions in minions_to_choose_from
    # make_golden should only be used on default minions (it doubles stats and sets minion.golden = True)
    # returns the actually summoned minions
    def try_summon_minions(self, minions_to_choose_from, how_many, summoner,
                           make_golden=False, after_death_collection=True, ignore_khadgar=False):
        summoned_minions = []
        for _ in range(how_many):
            if self.room_to_summon(after_death_collection):
                iterations_left = self.get_khadgar_multiplier() - 1
                cur = random.choice(minions_to_choose_from).get_copy()

                if make_golden:
                    cur.attack *= 2
                    cur.health *= 2
                    cur.golden = True

                if after_death_collection:
                    if len(self.board) != 0:  # non empty board
                        if summoner.minionToRightBeforeDeath == self.board[0]:  # summoner at end of board
                            idx = len(self.board)
                        else:
                            if summoner.minionToRightBeforeDeath is not None:  # normal deathrattle case
                                idx = self.board.index(summoner.minionToRightBeforeDeath)
                            else:
                                if summoner in self.board:
                                    idx = self.board.index(summoner) + 1
                                else:
                                    idx = 0  # TODO oder len(self.board)?
                    else:  # empty board
                        idx = 0
                else:
                    idx = self.board.index(summoner) + 1

                self.board.insert(idx, cur)
                self.log(str(summoner) + " summoned " + str(cur) + " at position " + str(idx) + ".")
                for m in self.board:
                    if TriggerCombat.ON_FRIENDLY_SUMMON in m.triggerCombat and m != cur:
                        self.log(str(m) + " triggers its 'on friendly summon' effect.")
                        m.on_friendly_summon(cur)
                summoned_minions.append(cur)

                if not ignore_khadgar:
                    for _ in range(iterations_left):
                        if self.room_to_summon(after_death_collection):
                            cur2 = cur.get_copy()
                            self.board.insert(idx, cur2)
                            self.log(str(cur) + " got copied by Khadgar.")
                            for m in self.board:
                                if TriggerCombat.ON_FRIENDLY_SUMMON in m.triggerCombat and m != cur2:
                                    self.log(str(m) + " triggers its 'on friendly summon' effect.")
                                    m.on_friendly_summon(cur)
                            summoned_minions.append(cur2)
                        else:
                            self.log("Khadgar couldn't copy " + str(cur) + " because there wasn't enough room.")
            else:
                self.log(str(summoner) + " tried to summon but there wasn't enough room.")

        for m in summoned_minions:
            m.combatant = self
        return summoned_minions

    def room_to_summon(self, after_death_collection):
        if not after_death_collection:
            return len(self.board) < 7
        # len("board without the dead minions") < 7
        return len(list(filter(lambda m: m not in self.combat.minions_removed_from_board, self.board))) < 7

    def activate_deathrattles_if_existent(self, dead_minion, ignore_baron=False):
        if ignore_baron:
            n = 1
        else:
            n = self.get_baron_multiplier()
        for _ in range(n):
            if Keyword.DEATHRATTLE in dead_minion.keywords:
                self.log(str(dead_minion) + " triggers its deathrattle effect.")
                dead_minion.deathrattle()
        for _ in range(n):
            if Keyword.MENACE in dead_minion.keywords:
                self.log(str(dead_minion) + " triggers its Replicating Menace deathrattle effect.")
                self.try_summon_minions([Microbot()], 3 * dead_minion.keywords.count(Keyword.MENACE), dead_minion)
            if Keyword.GOLDENMENACE in dead_minion.keywords:
                self.log(str(dead_minion) + " triggers its golden Replicating Menace deathrattle effect.")
                self.try_summon_minions([Microbot()], 3 * dead_minion.keywords.count(Keyword.MENACE), dead_minion, True)
        for _ in range(n):
            if Keyword.PLANTS in dead_minion.keywords:
                self.log(str(dead_minion) + " triggers its Plants deathrattle effect.")
                self.try_summon_minions([Plant()], 2 * dead_minion.keywords.count(Keyword.PLANTS), dead_minion)

    def get_baron_multiplier(self):
        n = 1
        for m in self.board:
            if isinstance(m, BaronRivendare):
                if n == 1:
                    n = 2
                if m.golden:
                    n = 3
                    break
        return n

    def get_khadgar_multiplier(self):
        n = 1
        for m in self.board:
            if isinstance(m, Khadgar) and m not in self.combat.minions_removed_from_board:
                n2 = 2
                if m.golden:
                    n2 = 3
                n *= n2
        return n

    # loops around
    def get_next_right_minion(self, minion):
        idx = self.board.index(minion)
        if idx == len(self.board) - 1:
            return self.board[0]
        return self.board[idx + 1]

    def add_to_whenever_or_after_dies_trigger_list(self, to_add):
        self.combat.add_to_whenever_or_after_dies_trigger_list(to_add)  # Junkbot, Qiraji, Hyena, Juggler

    def add_to_after_trigger_list(self, to_add):
        self.combat.add_to_after_trigger_list(to_add)  # BarrensBlacksmith, Bolvar, Drakonid, Togwaggle

    def add_to_extra_attack_requests(self, to_add):
        self.combat.add_to_extra_attack_requests(to_add)  # YoHoOgre

    def log(self, text):
        self.combat.log(text)

    def __str__(self):
        s = "Player " + str(self.player.playerNo) + ":\n\n"

        if len(self.board) == 0:
            s += "   Nothing on board ¯\\_(ツ)_/¯\n"
        for m in self.board:
            s += "   " + str(m) + "\n"

        return s
