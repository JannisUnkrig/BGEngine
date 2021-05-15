import random
import time

from Simulator.Combatant import Combatant
from Simulator.Minion import TriggerCombat, Keyword


class Combat:

    def __init__(self, p1, p2, game, has_consequences=True):
        # game logic
        self.c1 = Combatant(p1, None, self)
        self.c2 = Combatant(p2, self.c1, self)
        self.c1.enemy = self.c2
        self.c1Turn = self.determine_if_c1_first()
        self.do_another_combat_step = True

        # technical stuff
        self.game = game
        self.has_consequences = has_consequences
        self.damage_dealt_or_taken = None  # pos if c1 won, neg if c2 won
        self._extraAttackRequests = []
        self._afterTriggerRequests = []
        self._wheneverOrAfterDiesTriggerRequests = []
        self.minions_removed_from_board = []
        self.start_of_combat_c1_turn = True
        if random.random() < 0.5:
            self.start_of_combat_c1_turn = False

    def start(self, mode="fast"):
        if mode == "fast":
            self.log("Started combat between Player " + str(self.c1.player.playerNo) + " and Player "
                     + str(self.c2.player.playerNo) + ".")
            while self.do_another_combat_step:
                self.step()
        elif mode == "slow":
            self.log("Started combat between Player " + str(self.c1.player.playerNo) + " and Player "
                     + str(self.c2.player.playerNo) + " in slow mode.")
            while self.do_another_combat_step:
                self.disp(str(self))
                time.sleep(1)
                self.step()
        elif mode == "debug":
            self.disp(str(self))
            self.log("Started combat between Player " + str(self.c1.player.playerNo) + " and Player "
                     + str(self.c2.player.playerNo) + " in debug mode.")

    def step(self):
        if self.combat_is_over():
            self.log("Combat is over.")
            self.calc_and_deal_player_dmg()
            self.update_player_histories()
            if self.game.playersRemaining <= 1:
                for p in self.game.players:
                    if p.alive:
                        p.placing = 1
                self.game.over = True
                self.log(self.game.get_standings())
            self.do_another_combat_step = False
            self.game.curCombat = None
            return

        if len(self.c1.start_of_combat_effect_minions) > 0 or len(self.c2.start_of_combat_effect_minions) > 0:
            if self.start_of_combat_c1_turn:
                self.c1.activate_next_start_of_combat_effect()
                self.start_of_combat_c1_turn = False
            else:
                self.c2.activate_next_start_of_combat_effect()
                self.start_of_combat_c1_turn = True
            return

        if self.c1Turn:
            self.c1.attack()
            self.c1Turn = False
        else:
            self.c2.attack()
            self.c1Turn = True

    # ############################# Helpers ############################# #

    def clean_up(self):
        # no minion died
        all_minions_on_board = self.all_minions_on_board()
        if not any(m.is_dead() for m in all_minions_on_board):
            for m in all_minions_on_board:
                self.set_minion_to_right_before_death(m)
            self.resolve_after_trigger_list()
            return

        # atleast one minion died
        dead_cur_block = []
        dead_this_call = []
        if random.random() < 0.5:
            board1 = self.c1.board
            board2 = self.c2.board
        else:
            board1 = self.c2.board
            board2 = self.c1.board

        for _ in range(500):  # actual termination condition in body
            # cluttered writing because loop often runs only one time, so the performance plus is worth it
            if all_minions_on_board is not None:
                for m in all_minions_on_board:
                    self.set_minion_to_right_before_death(m)
                all_minions_on_board = None
            else:
                amob = self.all_minions_on_board()
                for m in amob:
                    self.set_minion_to_right_before_death(m)

            self.resolve_whenever_or_after_dies_trigger_list()
            dead_cur_block.clear()
            dead_cur_block.extend(list(filter(lambda m: m.is_dead() and
                                              m not in self.minions_removed_from_board, board1)))
            dead_cur_block.extend(list(filter(lambda m: m.is_dead() and
                                              m not in self.minions_removed_from_board, board2)))
            self.minions_removed_from_board.extend(dead_cur_block)
            dead_this_call.extend(dead_cur_block)
            for m in dead_cur_block:
                self.log(str(m) + " died.")
                m.health = -100000
            for dead_minion in dead_cur_block:
                curCombatant = dead_minion.combatant
                for m in curCombatant.board:
                    if TriggerCombat.ON_AND_AFTER_FRIENDLY_GETS_KILLED in m.triggerCombat and m != dead_minion:
                        m.on_and_after_friendly_gets_killed(dead_minion)
                curCombatant.activate_deathrattles_if_existent(dead_minion)
            for m in dead_cur_block:
                m.combatant.graveyard.append(m)
            for m in dead_cur_block:
                if Keyword.REBORN in m.keywords:
                    copy = type(m)()
                    copy.golden = m.golden
                    if copy.golden:
                        copy.attack *= 2
                    copy.health = 1
                    if Keyword.REBORN in copy.keywords:
                        copy.keywords.remove(Keyword.REBORN)
                    self.log(str(m) + " gets reborn.")
                    m.combatant.try_summon_minions([copy], 1, m)
                if m.isUpcomingAttacker:
                    m.combatant.pass_upcoming_attacker(m)

            amob = self.all_minions_on_board()
            for m in amob:
                self.reset_minion_to_right_before_death(m)

            self.resolve_after_trigger_list()

            # actual termination condition
            if len(dead_cur_block) == 0:
                break

        for m in dead_this_call:
            m.combatant.board.remove(m)

    def set_minion_to_right_before_death(self, minion):
        minion.minionToRightBeforeDeath = minion.combatant.get_next_right_minion(minion)

    def reset_minion_to_right_before_death(self, minion):
        minion.minionToRightBeforeDeath = None

    def all_minions_on_board(self):
        amob = []
        amob.extend(self.c1.board)
        amob.extend(self.c2.board)
        return amob

    def add_to_whenever_or_after_dies_trigger_list(self, to_add):
        self._wheneverOrAfterDiesTriggerRequests.append(to_add)  # Junkbot, Qiraji, Hyena, Juggler

    def add_to_after_trigger_list(self, to_add):
        self._afterTriggerRequests.append(to_add)  # BarrensBlacksmith, Bolvar, Drakonid, Togwaggle

    def add_to_extra_attack_requests(self, to_add):
        self._extraAttackRequests.append(to_add)  # YoHoOgre

    def resolve_whenever_or_after_dies_trigger_list(self):
        c = self._wheneverOrAfterDiesTriggerRequests.copy()
        self._wheneverOrAfterDiesTriggerRequests.clear()
        for m in c:
            self.log(str(m) + " triggers its 'whenever/after a friendly minion dies' effect.")
            m.resolve_effect()

    def resolve_after_trigger_list(self):
        c = self._afterTriggerRequests.copy()
        self._afterTriggerRequests.clear()
        for m in c:
            self.log(str(m) + " resolves its effect.")
            m.resolve_effect()

    def resolve_extra_attack_list(self):
        c = self._extraAttackRequests.copy()
        self._extraAttackRequests.clear()
        for m in c:
            if m.is_alive():
                self.log(str(m) + " gets its extra attack in.")
                m.resolve_effect()

    def determine_if_c1_first(self):
        if len(self.c1.board) > len(self.c2.board) \
                or (len(self.c1.board) == len(self.c2.board) and random.random() < 0.5):
            return True
        return False

    def combat_is_over(self):
        if len(self.c1.board) == 0 or len(self.c2.board) == 0:
            return True  # One side is empty
        if any(minion.attack > 0 for minion in self.c1.board) or any(minion.attack > 0 for minion in self.c2.board):
            return False  # One side has a minion with attack > 0
        return True  # Both sides only have minions with 0 attack

    def calc_and_deal_player_dmg(self):
        # draw
        if (len(self.c1.board) == 0 and len(self.c2.board) == 0) or (len(self.c1.board) > 0 and len(self.c2.board) > 0):
            self.damage_dealt_or_taken = 0
            self.log("Player " + str(self.c1.player.playerNo) + " and Player " + str(self.c2.player.playerNo)
                     + " tied.")
        # c1 won
        elif len(self.c2.board) == 0:
            dmg = self.c1.player.tavern.tier
            for m in self.c1.board:
                dmg += m.tier
            if self.has_consequences:
                self.c2.player.health -= dmg
            self.damage_dealt_or_taken = dmg
            self.log("Player " + str(self.c1.player.playerNo) + " dealt " + str(dmg) + " damage to Player "
                     + str(self.c2.player.playerNo) + ".")
            if self.c2.player.health <= 0 and self.c2.player.alive:
                self.c2.player.alive = False
                self.c2.player.placing = self.game.playersRemaining
                self.game.playersRemaining -= 1
                self.log("Player " + str(self.c2.player.playerNo) + " died (" + str(self.c2.player.placing) +
                         ". Place).")
        # c2 won
        else:
            dmg = self.c2.player.tavern.tier
            for m in self.c2.board:
                dmg += m.tier
            if self.has_consequences:
                self.c1.player.health -= dmg
            self.damage_dealt_or_taken = dmg * -1
            self.log("Player " + str(self.c2.player.playerNo) + " dealt " + str(dmg) + " damage to Player "
                     + str(self.c1.player.playerNo) + ".")
            if self.c1.player.health <= 0 and self.c1.player.alive:
                self.c1.player.alive = False
                self.c1.player.placing = self.game.playersRemaining
                self.game.playersRemaining -= 1
                self.log("Player " + str(self.c1.player.playerNo) + " died (" + str(self.c1.player.placing) +
                         ". Place).")

    def update_player_histories(self):
        self.c1.player.enemy_history.append(self.c2.player)
        self.c2.player.enemy_history.append(self.c1.player)
        self.c1.player.damage_history.append(self.damage_dealt_or_taken)
        self.c2.player.damage_history.append(self.damage_dealt_or_taken * -1)

    def log(self, text):
        self.game.log(text)

    # use sparingly. Display updates should be done in mf if possible
    def disp(self, text):
        self.game.disp(text)

    def __str__(self):
        return str(self.c2) + "\n\nVs.\n\n\n" + str(self.c1)
