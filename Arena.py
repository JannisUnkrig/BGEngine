from functools import partial
from time import sleep
from random import random, choice
from Minions import Keyword, TriggerCombat


class Arena:

    def __init__(self, mf):
        self.mf = mf  # main frame
        self.aq = []  # action queue
        self.doLog = False
        self.p1 = None
        self.p2 = None

        self.p1Turn = True
        self.b1 = []
        self.b2 = []
        self.b1Index = 0
        self.b2Index = 0

        self.startOfCombat = True
        self.startOfCombatP1Turn = True
        self.startOfCombatB1Index = 0
        self.startOfCombatB2Index = 0

        self.dmg = None

        # combat trigger (afterAttack, afterSurviveAttack and onTakeDamage don't need a list as they're only triggered
        # by the minion itself)
        self._p1OnAttack = []
        self._p1OnGetAttacked = []
        self._p1OnKill = []
        self._p1OnGetKilled = []
        self._p1AfterGetKilled = []
        self._p1OnStartOfCombat = []
        self._p1AfterLoseDivineShield = []
        self._p1OnSummon = []
        self._p1AfterSummon = []

        self._p2OnAttack = []
        self._p2OnGetAttacked = []
        self._p2OnKill = []
        self._p2OnGetKilled = []
        self._p2AfterGetKilled = []
        self._p2OnStartOfCombat = []
        self._p2AfterLoseDivineShield = []
        self._p2OnSummon = []
        self._p2AfterSummon = []

    def combatphase(self, players):
        for p in players:
            p.end_of_turn()
        # TODO
        for p in players:
            p.start_of_turn()
        return ""

    def battle(self, p1, p2, mode="fast"):
        # Setup Arena
        self.aq = []
        self.p1 = p1
        self.p2 = p2
        if p1.get_board_size() > p2.get_board_size() or (p1.get_board_size() == p2.get_board_size() and random() < 0.5):
            self.p1Turn = True
        else:
            self.p1Turn = False

        self.b1 = p1.get_board_copy()
        self.b2 = p2.get_board_copy()
        self.clear_trigger_lists()
        self.add_to_trigger_list(self.b1, self.p1)
        self.add_to_trigger_list(self.b2, self.p2)
        self.b1Index = 0
        self.b2Index = 0

        self.startOfCombat = True
        if random() < 0.5:
            self.startOfCombatP1Turn = True
        else:
            self.startOfCombatP1Turn = False
        self.startOfCombatB1Index = 0
        self.startOfCombatB2Index = 0

        self.dmg = None

        # Execute Combat steps
        if mode == "fast":
            while self.dmg is None:
                self.step()
        elif mode == "slow":
            self.doLog = True
            self.disp(str(self))
            while self.dmg is None:
                sleep(1)
                self.step()
        elif mode == "debug":
            self.doLog = True
            self.disp(str(self))
            self.log("Started combat between Player " + str(self.p1.playerNo) + " and Player " + str(self.p2.playerNo)
                     + " in debug mode (Use \"step\" to continue).")

    def step(self):
        # if combat is over calc damage and return
        if not self.combat_still_going():
            self.log("Combat is over.")
            if self.dmg is None:
                self.calc_dmg()
            return

        # start of combat stuff
        if self.startOfCombat and (len(self._p1OnStartOfCombat) > 0 or len(self._p1OnStartOfCombat) > 0):
            # TODO
            return

        # attack
        if self.p1Turn:
            attacking_minion = self.b1[self.b1Index]
            attacked_board = self.b2
        else:
            attacking_minion = self.b2[self.b2Index]
            attacked_board = self.b1
        self.attack(attacking_minion, attacked_board)

        # resolve queued actions and clean up dead minions until no actions are queued
        while True:
            self.resolve_queue()
            # self.clean_up()
            if len(self.aq) <= 0:
                break

        # update attacking index & who's turn it is
        if len(self.b1) > 0 and len(self.b2) > 0:
            if self.p1Turn:
                self.b1Index = (self.b1Index + 1) % len(self.b1)
                self.p1Turn = False
            else:
                self.b2Index = (self.b2Index + 1) % len(self.b2)
                self.p1Turn = True

        # display current combat state
        if self.doLog:
            self.disp(str(self))

    # ############################# Helpers ############################# #

    def enqueue(self, f, *args):
        self.aq.append(partial(f, *args))

    def enqueue_at_start(self, f, *args):
        self.aq.insert(0, partial(f, *args))

    def resolve_queue(self):
        while len(self.aq) > 0:
            self.aq.pop(0)()

    def clean_up(self):
        if self.p1Turn:
            for dead in self.b2:
                if dead.health <= 0:
                    self.log(str(dead) + " died.")
                    for m in self._p2OnGetKilled:
                        self.log(str(m) + " triggers its 'whenever a friendly minion dies' effect.")
                        m.on_get_killed(dead)
                    for m in self._p1OnKill:
                        self.log(str(m) + " triggers its 'whenever a friendly minion kills an enemy' effect.")
                        m.on_kill(dead.killedBy)

                    idx_of_dead = self.b2.index(dead)
                    self.b2.remove(dead)
                    self.log(str(dead) + " was removed from the board.")

                    self.remove_from_trigger_list([dead], self.p2)

                    if idx_of_dead < self.b1Index:
                        self.b1Index -= 1
                    if len(self.b2) > 0:
                        self.b2Index %= len(self.b2)

                    for m in self._p2AfterGetKilled:
                        self.log(str(m) + " triggers its 'after a friendly minion dies' effect.")
                        m.after_get_killed(dead, self.b1, self.b2, idx_of_dead)
                    if Keyword.DEATHRATTLE in dead.keywords:
                        self.log(str(dead) + " triggers its deathrattle effect.")
                        dead.deathrattle(self, idx_of_dead, self.b2, self.b1)
                    if Keyword.REBORN in dead.keywords:
                        self.log(str(dead) + " triggers its reborn effect.")
                        m = type(dead)()
                        m.health = 1
                        self.enqueue(self.summon, [dead], m, self.b2, idx_of_dead)

        else:
            for dead in self.b1:
                if dead.health <= 0:
                    self.log(str(dead) + " died.")
                    for m in self._p1OnGetKilled:
                        self.log(str(m) + " triggers its 'whenever a friendly minion dies' effect.")
                        m.on_get_killed(dead)
                    for m in self._p2OnKill:
                        self.log(str(m) + " triggers its 'whenever a friendly minion kills an enemy' effect.")
                        m.on_kill(dead.killedBy)

                    idx_of_dead = self.b1.index(dead)
                    self.b1.remove(dead)
                    self.log(str(dead) + " was removed from the board.")

                    self.remove_from_trigger_list([dead], self.p1)

                    if idx_of_dead < self.b1Index:
                        self.b1Index -= 1
                    if len(self.b1) > 0:
                        self.b1Index %= len(self.b1)

                    for m in self._p1AfterGetKilled:
                        self.log(str(m) + " triggers its 'after a friendly minion dies' effect.")
                        m.after_get_killed(dead, self.b2, self.b1, idx_of_dead)
                    if Keyword.DEATHRATTLE in dead.keywords:
                        self.log(str(dead) + " triggers its deathrattle effect.")
                        dead.deathrattle(self, idx_of_dead, self.b1, self.b2)
                    if Keyword.REBORN in dead.keywords:
                        self.log(str(dead) + " triggers its reborn effect.")
                        m = type(dead)()
                        m.health = 1
                        self.enqueue(self.summon, [dead], m, self.b1, idx_of_dead)

    def attack(self, attacking_minion, attacked_board):
        target = self.get_attack_target(attacked_board)
        if self.doLog:
            self.log(str(attacking_minion) + " attacks " + str(target))

        if attacked_board == self.b2:
            for m in self._p2OnGetAttacked:
                self.log(str(m) + " triggers its 'whenever a friendly minion is attacked' effect.")
                m.on_get_attacked(target, self.b2)
            for m in self._p1OnAttack:
                self.log(str(m) + " triggers its 'whenever a friendly minion attacks' effect.")
                m.on_attack(attacking_minion, self.b1)
        else:
            for m in self._p1OnGetAttacked:
                self.log(str(m) + " triggers its 'whenever a friendly minion is attacked' effect.")
                m.on_get_attacked(target, self.b1)
            for m in self._p2OnAttack:
                self.log(str(m) + " triggers its 'whenever a friendly minion attacks' effect.")
                m.on_attack(attacking_minion, self.b2)

        self.take_damage(attacking_minion.attack, target, attacking_minion)
        self.take_damage(target.attack, attacking_minion, target)

        if attacked_board == self.b2:
            if TriggerCombat.AFTER_SURVIVE_ATTACK in target.triggerCombat and target.health > 0:
                self.log(str(target) + " triggers its 'after survive attack' effect.")
                target.after_survive_attack(self.b1)
            if TriggerCombat.AFTER_ATTACK in attacking_minion.triggerCombat:
                self.log(str(attacking_minion) + " triggers its 'after attack' effect.")
                attacking_minion.after_attack(self.b1, self.b2, self.p1)
        else:
            if TriggerCombat.AFTER_SURVIVE_ATTACK in target.triggerCombat and target.health > 0:
                self.log(str(target) + " triggers its 'after survive attack' effect.")
                target.after_survive_attack(self.b2)
            if TriggerCombat.AFTER_ATTACK in attacking_minion.triggerCombat:
                self.log(str(attacking_minion) + " triggers its 'after attack' effect.")
                attacking_minion.after_attack(self.b2, self.b1, self.p2)

        self.enqueue(self.clean_up())

    def get_attack_target(self, board):
        taunts = []
        for m in board:
            if Keyword.TAUNT in m.keywords:
                taunts.append(m)
        if len(taunts) == 0:
            return choice(board)
        else:
            return choice(taunts)

    def take_damage(self, how_much, who, by):
        if how_much <= 0:
            return

        if who in self.b1:
            dmg_p1 = True  # p1's minion took damage
        else:
            dmg_p1 = False  # p2's minion took damage

        # handle divine shield
        if Keyword.DIVINE_SHIELD in who.keywords:
            who.keywords.remove(Keyword.DIVINE_SHIELD)
            self.log(str(who) + " lost his divine shield.")
            if dmg_p1:
                for m in self._p1AfterLoseDivineShield:
                    self.log(str(m) + " triggers its 'after a friendly minion loses divine shield' effect.")
                    m.after_lose_divine_shield()
            else:
                for m in self._p2AfterLoseDivineShield:
                    self.log(str(m) + " triggers its 'after a friendly minion loses divine shield' effect.")
                    m.after_lose_divine_shield()
        else:
            # before dealing damage
            if dmg_p1:
                if TriggerCombat.ON_TAKE_DAMAGE in who.triggerCombat:
                    self.log(str(who) + " triggers its 'whenever this minion takes damage' effect.")
                    who.on_take_damage(self.b1)
            else:
                if TriggerCombat.ON_TAKE_DAMAGE in who.triggerCombat:
                    self.log(str(who) + " triggers its 'whenever this minion takes damage' effect.")
                    who.on_take_damage(self.b2)

            # deal damage
            who.health -= how_much
            if self.doLog:
                self.log(str(who) + " took " + str(how_much) + " damage.")

            # poison
            if Keyword.POISONOUS in by.keywords:
                who.health = -10000  # würde Probleme machen wenn es iwann einen minion mit Poisonous und Overkill gibt
                self.log(str(who) + " was poisoned.")

            # after dealing damage
            if dmg_p1:
                if Keyword.FRENZY in who.keywords and who.health > 0:
                    self.log(str(who) + " triggers its frenzy effect.")
                    who.frenzy(self.b1)
                if Keyword.OVERKILL in by.keywords and who.health < 0:
                    self.log(str(by) + " triggers its overkill effect.")
                    by.overkill(self.b2, self.b1)
            else:
                if Keyword.FRENZY in who.keywords and who.health > 0:
                    self.log(str(who) + " triggers its frenzy effect.")
                    who.frenzy(self.b2)
                if Keyword.OVERKILL in by.keywords and who.health < 0:
                    self.log(str(by) + " triggers its overkill effect.")
                    by.overkill(self.b1, self.b2)

            if who.health <= 0:
                who.killedBy = by

    def buff(self, who, attack, health):
        who.attack += attack
        who.health += health
        self.log(str(who) + " got buffed with +" + str(attack) + " / +" + str(health))

    def summon(self, summoners, summoned, board, position):  # TODO indexe updaten
        if len(board) >= 7:
            if self.doLog:
                self.log("The summon failed because the board is full.")
            return

        if board == self.b1:
            for m in self._p1OnSummon:
                self.log(str(m) + " triggers its 'whenever a friendly minion is summoned' effect.")
                m.on_summon(summoned)
        else:
            for m in self._p2OnSummon:
                self.log(str(m) + " triggers its 'whenever a friendly minion is summoned' effect.")
                m.on_summon(summoned)

        board.insert(position, summoned)
        self.log(str(summoned) + " was added to the board at position " + str(position))

        if board == self.b1:
            self.add_to_trigger_list([summoned], self.p1)
        else:
            self.add_to_trigger_list([summoned], self.p2)

        if board == self.b1:
            for m in self._p1AfterSummon:
                self.log(str(m) + " triggers its 'after a friendly minion is summoned' effect.")
                m.after_summon(self, summoners, summoned, self.b1, position, self.b2)
        else:
            for m in self._p2AfterSummon:
                self.log(str(m) + " triggers its 'after a friendly minion is summoned' effect.")
                m.after_summon(self, summoners, summoned, self.b2, position, self.b1)

    def combat_still_going(self):
        if len(self.b1) == 0 or len(self.b2) == 0:
            return False
        if any(minion.attack > 0 for minion in self.b1) or any(minion.attack > 0 for minion in self.b2):
            return True
        return False

    def calc_dmg(self):
        # draw
        if (len(self.b1) == 0 and len(self.b2) == 0) or (len(self.b1) > 0 and len(self.b2) > 0):
            self.dmg = 0
            self.log("Player " + str(self.p1.playerNo) + " and Player " + str(self.p2.playerNo) + " tied.")
        # p1 won
        elif len(self.b2) == 0:
            self.dmg = self.p1.tavern.tier
            for m in self.b1:
                self.dmg += m.tier
            self.log("Player " + str(self.p1.playerNo) + " dealt " + str(self.dmg) + " to Player "
                     + str(self.p2.playerNo) + ".")
        # p2 won
        else:
            self.dmg = self.p2.tavern.tier
            for m in self.b2:
                self.dmg += m.tier
            self.log("Player " + str(self.p2.playerNo) + " dealt " + str(self.dmg) + " to Player "
                     + str(self.p1.playerNo) + ".")
            self.dmg *= -1

    def add_to_trigger_list(self, minions, p):
        if p == self.p1:
            for minion in minions:
                if TriggerCombat.ON_ATTACK in minion.triggerCombat:
                    self._p1OnAttack.append(minion)
                if TriggerCombat.ON_GET_ATTACKED in minion.triggerCombat:
                    self._p1OnGetAttacked.append(minion)
                if TriggerCombat.ON_KILL in minion.triggerCombat:
                    self._p1OnKill.append(minion)
                if TriggerCombat.ON_GET_KILLED in minion.triggerCombat:
                    self._p1OnGetKilled.append(minion)
                if TriggerCombat.AFTER_GET_KILLED in minion.triggerCombat:
                    self._p1AfterGetKilled.append(minion)
                if TriggerCombat.ON_START_OF_COMBAT in minion.triggerCombat:
                    self._p1OnStartOfCombat.append(minion)
                if TriggerCombat.AFTER_LOSE_DIVINE_SHIELD in minion.triggerCombat:
                    self._p1AfterLoseDivineShield.append(minion)
                if TriggerCombat.ON_SUMMON in minion.triggerCombat:
                    self._p1OnSummon.append(minion)
                if TriggerCombat.AFTER_SUMMON in minion.triggerCombat:
                    self._p1AfterSummon.append(minion)
        elif p == self.p2:
            for minion in minions:
                if TriggerCombat.ON_ATTACK in minion.triggerCombat:
                    self._p2OnAttack.append(minion)
                if TriggerCombat.ON_GET_ATTACKED in minion.triggerCombat:
                    self._p2OnGetAttacked.append(minion)
                if TriggerCombat.ON_KILL in minion.triggerCombat:
                    self._p2OnKill.append(minion)
                if TriggerCombat.ON_GET_KILLED in minion.triggerCombat:
                    self._p2OnGetKilled.append(minion)
                if TriggerCombat.AFTER_GET_KILLED in minion.triggerCombat:
                    self._p2AfterGetKilled.append(minion)
                if TriggerCombat.ON_START_OF_COMBAT in minion.triggerCombat:
                    self._p2OnStartOfCombat.append(minion)
                if TriggerCombat.AFTER_LOSE_DIVINE_SHIELD in minion.triggerCombat:
                    self._p2AfterLoseDivineShield.append(minion)
                if TriggerCombat.ON_SUMMON in minion.triggerCombat:
                    self._p2OnSummon.append(minion)
                if TriggerCombat.AFTER_SUMMON in minion.triggerCombat:
                    self._p2AfterSummon.append(minion)

    def remove_from_trigger_list(self, minions, p):
        if p == self.p1:
            for minion in minions:
                if TriggerCombat.ON_ATTACK in minion.triggerCombat:
                    self._p1OnAttack.remove(minion)
                if TriggerCombat.ON_GET_ATTACKED in minion.triggerCombat:
                    self._p1OnGetAttacked.remove(minion)
                if TriggerCombat.ON_KILL in minion.triggerCombat:
                    self._p1OnKill.remove(minion)
                if TriggerCombat.ON_GET_KILLED in minion.triggerCombat:
                    self._p1OnGetKilled.remove(minion)
                if TriggerCombat.AFTER_GET_KILLED in minion.triggerCombat:
                    self._p1AfterGetKilled.remove(minion)
                if TriggerCombat.ON_START_OF_COMBAT in minion.triggerCombat:
                    self._p1OnStartOfCombat.remove(minion)
                if TriggerCombat.AFTER_LOSE_DIVINE_SHIELD in minion.triggerCombat:
                    self._p1AfterLoseDivineShield.remove(minion)
                if TriggerCombat.ON_SUMMON in minion.triggerCombat:
                    self._p1OnSummon.remove(minion)
                if TriggerCombat.AFTER_SUMMON in minion.triggerCombat:
                    self._p1AfterSummon.remove(minion)
        elif p == self.p2:
            for minion in minions:
                if TriggerCombat.ON_ATTACK in minion.triggerCombat:
                    self._p2OnAttack.remove(minion)
                if TriggerCombat.ON_GET_ATTACKED in minion.triggerCombat:
                    self._p2OnGetAttacked.remove(minion)
                if TriggerCombat.ON_KILL in minion.triggerCombat:
                    self._p2OnKill.remove(minion)
                if TriggerCombat.ON_GET_KILLED in minion.triggerCombat:
                    self._p2OnGetKilled.remove(minion)
                if TriggerCombat.AFTER_GET_KILLED in minion.triggerCombat:
                    self._p2AfterGetKilled.remove(minion)
                if TriggerCombat.ON_START_OF_COMBAT in minion.triggerCombat:
                    self._p2OnStartOfCombat.remove(minion)
                if TriggerCombat.AFTER_LOSE_DIVINE_SHIELD in minion.triggerCombat:
                    self._p2AfterLoseDivineShield.remove(minion)
                if TriggerCombat.ON_SUMMON in minion.triggerCombat:
                    self._p2OnSummon.remove(minion)
                if TriggerCombat.AFTER_SUMMON in minion.triggerCombat:
                    self._p2AfterSummon.remove(minion)

    def clear_trigger_lists(self):
        self._p1OnAttack = []
        self._p1OnGetAttacked = []
        self._p1OnKill = []
        self._p1OnGetKilled = []
        self._p1AfterGetKilled = []
        self._p1OnStartOfCombat = []
        self._p1AfterLoseDivineShield = []
        self._p1OnSummon = []
        self._p1AfterSummon = []

        self._p2OnAttack = []
        self._p2OnGetAttacked = []
        self._p2OnKill = []
        self._p2OnGetKilled = []
        self._p2AfterGetKilled = []
        self._p2OnStartOfCombat = []
        self._p2AfterLoseDivineShield = []
        self._p2OnSummon = []
        self._p2AfterSummon = []

    def log(self, text):
        if self.doLog:
            self.mf.add_to_log(text)

    def disp(self, text):
        if self.doLog:
            self.mf.show_on_monitor(text)

    def __str__(self):
        s = "Player " + str(self.p1.playerNo) + " Vs. Player " + str(self.p2.playerNo) + ":\n\n"

        if len(self.b1) == 0:
            s += "nothing ¯\\_(ツ)_/¯\n"
        for m in self.b1:
            s += str(m) + "\n"

        s += "\nVs.\n\n"

        if len(self.b2) == 0:
            s += "nothing ¯\\_(ツ)_/¯\n"
        for m in self.b2:
            s += str(m) + "\n"

        return s
