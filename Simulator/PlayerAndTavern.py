import random

from Simulator.Minion import Keyword, TriggerTavern, Minion
from Simulator.Minions.BrannBronzebeard import BrannBronzebeard
from Simulator.Minions.Khadgar import Khadgar
from Simulator.Spell import Spell
from Simulator.TripleReward import TripleReward


# ############################# Player ############################# #


class Player:

    def __init__(self, game):
        # technical stuff
        self.game = game
        self.validBcTarget = True
        self.after_bc_index = -1

        # game logic
        self.playerNo = -1
        self.health = 40
        self.alive = True
        self.placing = -1  # -1 == alive
        self.maxGold = 3
        self.gold = 3
        self.hand = []
        self._board = []
        self._max_board_size = 7
        self.discover_options = []
        self.tavern = Tavern(self)
        self.enemy_history = []
        self.damage_history = []

        # trigger lists
        self._onOrAfterPlay = []  # minion.after_play(player, minion)
        self._onSummon = []  # minion.on_summon(player, summoned)
        self.onBuy = []  # minion.on_buy(player, minion)
        self._onStartOfTurn = []  # minion.on_start_of_turn(player)
        self._onEndOfTurn = []  # minion.on_end_of_turn(player)
        self._onTakeHeroDamage = []  # minion.on_take_hero_damage(player)

    # ############################# Player Actions ############################# #

    def play(self, from_index=0, to_index=-1, target_index=0):
        if self.discovery_happening():
            self.log("The discovery needs to be completed first.")
            return
        if not 0 <= from_index < len(self.hand) or not 0 <= target_index < max(1, len(self._board)):
            self.log("Invalid indexes for playing the card.")
            return

        # if card is a Spell
        if isinstance(self.hand[from_index], Spell):
            spell = self.hand[from_index]
            if spell.cost > self.gold:
                self.log("Insufficient gold for casting this spell.")
                return
            self.log("Casting " + str(spell) + ".")
            spell.cast(self, target_index)
            return

        # played card is Minion
        if to_index == -1:
            to_index = len(self._board)
        if not 0 <= to_index < min(len(self._board) + 1, self._max_board_size):
            self.log("Invalid position for playing a minion with for the current board state.")
            return

        minion = self.hand[from_index]
        self.after_bc_index = to_index

        if Keyword.BATTLECRY in minion.keywords:
            self.validBcTarget = True
            n = self.get_brann_multiplier()
            for _ in range(n):
                self.log(str(minion) + " triggers its battlecry effect.")
                minion.battlecry(self, self.after_bc_index, target_index)
            if not self.validBcTarget:
                self.log("Invalid target for battlecry.")
                return

        self.hand.remove(minion)
        self._board.insert(self.after_bc_index, minion)

        for m in self._onOrAfterPlay:
            self.log(str(m) + " triggers its 'on/after play minion' effect.")
            m.on_or_after_play(self, minion)
        for m in self._onSummon:
            self.log(str(m) + " triggers its 'on summon' effect.")
            m.on_summon(self, minion)

        self.add_to_trigger_list(minion)
        if minion.golden:
            self.try_add_to_hand(TripleReward(self.tavern.tier))
        self.log("Played " + str(minion) + " to position " + str(self.after_bc_index) + ".")

    def move(self, pos, by):
        if self.discovery_happening():
            self.log("The discovery needs to be completed first.")
            return
        if not 0 <= pos < len(self._board) or not 0 <= pos + by < len(self._board):
            self.log("Invalid indexes for moving with the current board state.")
            return
        tmp = self._board.pop(pos)
        self._board.insert(pos + by, tmp)
        self.log("Moved " + str(tmp) + " " + str(by) + " to the right")

    def choose(self, choice_idx):
        if not self.discovery_happening():
            self.log("No discovery happening right now.")
            return
        if not 0 <= choice_idx < len(self.discover_options):
            self.log("Invalid discovery choice.")
            return

        choice = self.discover_options[choice_idx]
        self.discover_options.remove(choice)
        self.try_add_to_hand(choice)
        self.log("Discovered " + str(choice) + ".")

        self.game.minionPool.return_many(self.discover_options)
        self.discover_options = []

    def buy(self, index):
        if self.discovery_happening():
            self.log("The discovery needs to be completed first.")
            return
        self.tavern.buy(index)

    def sell(self, index):
        if self.discovery_happening():
            self.log("The discovery needs to be completed first.")
            return
        self.tavern.sell(index)

    def tier_up(self):
        if self.discovery_happening():
            self.log("The discovery needs to be completed first.")
            return
        self.tavern.tier_up()

    def roll(self):
        if self.discovery_happening():
            self.log("The discovery needs to be completed first.")
            return
        self.tavern.roll()

    def freeze(self):
        if self.discovery_happening():
            self.log("The discovery needs to be completed first.")
            return
        self.tavern.freeze()

    # ############################# Internal 'Happenings' ############################# #

    # only for setting up games for testing
    def appear_on_board(self, minion):
        self._board.append(minion)
        self.add_to_trigger_list(minion)

    def leave_board(self, minion):
        self.remove_from_trigger_list(minion)
        self._board.remove(minion)

    def buff(self, minion, attack, health):
        minion.attack += attack
        minion.health += health
        self.log("Buffed " + str(minion) + " with (" + str(attack) + "/" + str(health) + ").")

    # use make_golden only with default minions
    # setupgame 1 tabbycat, tabbycat, golden brannBronzebeard, golden khadgar, khadgar
    def try_summon(self, to_summon_minion, position, make_golden=False, leave_one_free_space=False):
        mbs = self._max_board_size
        if leave_one_free_space:
            mbs -= 1
        if len(self._board) >= mbs:
            return

        if make_golden:
            to_summon_minion.attack *= 2
            to_summon_minion.health *= 2
            to_summon_minion.golden = True

        self._board.insert(position, to_summon_minion)
        self.log("Summoned " + str(to_summon_minion) + " at position " + str(position) + ".")
        all_summoned = [to_summon_minion]
        position += 1

        for m in self._onSummon:
            self.log(str(m) + " triggers its 'on summon' effect.")
            m.on_summon(self, to_summon_minion)

        tripled_ex_positions = self.check_for_triple(to_summon_minion)
        tmp = 0
        for ex_pos in tripled_ex_positions:
            if ex_pos < position:
                tmp += 1
            if ex_pos < self.after_bc_index:
                self.after_bc_index -= 1
        position -= tmp

        iterations_left = self.get_khadgar_multiplier() - 1
        for _ in range(iterations_left):
            if len(self._board) < mbs:
                cur = to_summon_minion.get_copy()
                self._board.insert(position, cur)
                self.log(str(to_summon_minion) + " got copied to position " + str(position) + " by Khadgar.")
                all_summoned.append(cur)

                for m in self._onSummon:
                    self.log(str(m) + " triggers its 'on summon' effect.")
                    m.on_summon(self, cur)

                tripled_ex_positions = self.check_for_triple(cur)
                for ex_pos in tripled_ex_positions:
                    if ex_pos < position:
                        position -= 1
                    if ex_pos < self.after_bc_index:
                        self.after_bc_index -= 1
            else:
                self.log("Khadgar couldn't copy " + str(to_summon_minion) + " because there wasn't enough room.")

        for m in all_summoned:
            self.add_to_trigger_list(m)

    def take_hero_damage_on_own_turn(self, how_much):
        for m in self._onTakeHeroDamage:
            m.on_take_hero_damage(self)
        self.health -= how_much
        self.log("Player " + str(self.playerNo) + " took " + str(how_much) + " damage.")
        if self.health <= 0 and self.alive:
            self.alive = False
            self.placing = self.game.playersRemaining
            self.game.playersRemaining -= 1
            self.log("Player " + str(self.playerNo) + " died (" + str(self.placing) + ". Place).")

    def start_of_turn(self):
        for m in self._onStartOfTurn:
            self.log(str(m) + " triggers its 'on start of turn' effect.")
            m.on_start_of_turn(self)
        if self.maxGold < 10:
            self.maxGold += 1
        self.gold = self.maxGold
        self.tavern.start_of_turn()

    def end_of_turn(self):
        for m in self._onEndOfTurn:
            self.log(str(m) + " triggers its 'on end of turn' effect.")
            m.on_end_of_turn(self)

    # ############################# Helpers ############################# #

    def try_add_to_hand(self, card):
        if len(self.hand) < 10:
            self.hand.append(card)
            self.check_for_triple(card)
        else:
            self.log("Tried adding " + str(card) + " to the hand, but it was full.")

    def discovery_happening(self):
        if len(self.discover_options) == 0:
            return False
        return True

    def get_combat_board(self):
        c = []
        for i in range(len(self._board)):
            c.append(self._board[i].get_copy())
            c[i].realTwin = self._board[i]
        return c

    # don't add or remove minions this way
    def get_board(self):
        return self._board

    def get_board_size(self):
        return len(self._board)

    def get_minion(self, index):
        return self._board[index]

    # returns list in random order
    def get_one_minion_from_each_tribe_on_board(self):
        chosen_minions = []

        single_tribe_minions = list(filter(lambda m: len(m.tribe) == 1, self._board))
        random.shuffle(single_tribe_minions)
        for minion in single_tribe_minions:
            if not any(minion.tribe[0] in chosen_minion.tribe for chosen_minion in chosen_minions):
                chosen_minions.append(minion)

        all_tribe_minions = list(filter(lambda m: len(m.tribe) > 1, self._board))
        chosen_minions.extend(all_tribe_minions)

        random.shuffle(chosen_minions)
        return chosen_minions

    def adapt_randomly(self, minion):
        self.log(str(minion) + " adapts.")
        adaptation_no = random.random() * 8
        if adaptation_no < 1:
            if Keyword.DIVINESHIELD not in minion.keywords:
                minion.keywords.append(Keyword.DIVINESHIELD)
            self.log(str(minion) + " got Divine Shield.")
        elif 1 <= adaptation_no < 2:
            self.buff(minion, 3, 0)
        elif 2 <= adaptation_no < 3:
            minion.keywords.append(Keyword.PLANTS)
            self.log(str(minion) + " got \"Deathrattle: Summon two 1/1 Plants.\".")
        elif 3 <= adaptation_no < 4:
            if Keyword.WINDFURY not in minion.keywords:
                minion.keywords.append(Keyword.WINDFURY)
            self.log(str(minion) + " got Windfury.")
        elif 4 <= adaptation_no < 5:
            if Keyword.TAUNT not in minion.keywords:
                minion.keywords.append(Keyword.TAUNT)
            self.log(str(minion) + " got Taunt.")
        elif 5 <= adaptation_no < 6:
            self.buff(minion, 1, 1)
        elif 6 <= adaptation_no < 7:
            self.buff(minion, 0, 3)
        elif 7 <= adaptation_no < 8:
            if Keyword.POISONOUS not in minion.keywords:
                minion.keywords.append(Keyword.POISONOUS)
            self.log(str(minion) + " got Poisonous.")
        else:
            self.log("Error in adapt_randomly(minion) method in class Player")

    # returns the board indexes it took the minions from (if they even were on board).
    def check_for_triple(self, new_minion):
        candidates = []
        candidates.extend(self._board)
        candidates.extend(list(filter(lambda ms: isinstance(ms, Minion), self.hand)))
        matching = []
        for m in candidates:
            if m != new_minion and not m.golden and m.name == new_minion.name:
                matching.append(m)
                if len(matching) == 2:
                    golden_boy = type(new_minion)()
                    golden_boy.attack *= -1
                    golden_boy.health *= -1
                    golden_boy.golden = True

                    matching.append(new_minion)

                    taken_from_board_indexes = []
                    for m2 in matching:
                        if m2 in self._board:
                            taken_from_board_indexes.append(self._board.index(m2))

                    for m2 in matching:
                        if m2 in self._board:
                            self._board.remove(m2)
                            self.remove_from_trigger_list(m2)
                        else:
                            self.hand.remove(m2)
                        golden_boy.attack += m2.attack
                        golden_boy.health += m2.health

                    self.log("Tripled into " + str(golden_boy) + ".")
                    self.try_add_to_hand(golden_boy)
                    return taken_from_board_indexes
        return []

    def get_khadgar_multiplier(self):
        n = 1
        for m in self._board:
            if isinstance(m, Khadgar):
                n2 = 2
                if m.golden:
                    n2 = 3
                n *= n2
        return n

    def get_brann_multiplier(self):
        n = 1
        for m in self._board:
            if isinstance(m, BrannBronzebeard):
                n = 2
                if m.golden:
                    return 3
        return n

    def add_to_trigger_list(self, minion):
        if TriggerTavern.ON_OR_AFTER_PLAY in minion.triggerTavern:
            self._onOrAfterPlay.append(minion)
        if TriggerTavern.ON_SUMMON in minion.triggerTavern:
            self._onSummon.append(minion)
        if TriggerTavern.ON_BUY in minion.triggerTavern:
            self.onBuy.append(minion)
        if TriggerTavern.ON_START_OF_TURN in minion.triggerTavern:
            self._onStartOfTurn.append(minion)
        if TriggerTavern.ON_END_OF_TURN in minion.triggerTavern:
            self._onEndOfTurn.append(minion)
        if TriggerTavern.ON_TAKE_HERO_DAMAGE in minion.triggerTavern:
            self._onTakeHeroDamage.append(minion)

    def remove_from_trigger_list(self, minion):
        if TriggerTavern.ON_OR_AFTER_PLAY in minion.triggerTavern:
            self._onOrAfterPlay.remove(minion)
        if TriggerTavern.ON_SUMMON in minion.triggerTavern:
            self._onSummon.remove(minion)
        if TriggerTavern.ON_BUY in minion.triggerTavern:
            self.onBuy.remove(minion)
        if TriggerTavern.ON_START_OF_TURN in minion.triggerTavern:
            self._onStartOfTurn.remove(minion)
        if TriggerTavern.ON_END_OF_TURN in minion.triggerTavern:
            self._onEndOfTurn.remove(minion)
        if TriggerTavern.ON_TAKE_HERO_DAMAGE in minion.triggerTavern:
            self._onTakeHeroDamage.remove(minion)

    def get_history(self):
        if len(self.enemy_history) == 0:
            return "No Fights logged yet."
        s = ""
        for i in range(len(self.enemy_history)):
            enemy = self.enemy_history[i]
            dmg = self.damage_history[i]
            s += "Round " + str(i + 1) + ": "
            if dmg > 0:
                s += "Dealt " + str(dmg) + " to Player " + str(enemy.playerNo) + "\n"
            elif dmg < 0:
                s += "Took " + str(dmg * -1) + " from Player " + str(enemy.playerNo) + "\n"
            else:
                s += "Tied with Player " + str(enemy.playerNo) + "\n"
        return s

    def log(self, text):
        self.game.log(text)

    def __str__(self):
        s = "Player " + str(self.playerNo) + ":\n   Gold: " + str(self.gold) + "/" + str(self.maxGold) + "   Health: " \
            + str(self.health) + "\n\n" + str(self.tavern) + "\n   Board:\n"
        if len(self._board) == 0:
            s += "      empty ¯\\_(ツ)_/¯\n"
        for m in self._board:
            s += "      " + str(m) + "\n"
        s += "\n   Hand:\n"
        if len(self.hand) == 0:
            s += "      empty ¯\\_(ツ)_/¯\n"
        for m in self.hand:
            s += "      " + str(m) + "\n"
        if self.discovery_happening():
            s += "\n\n   Discovery Options:\n"
            for o in self.discover_options:
                s += "      " + str(o) + "\n"
        return s

    def sorting_func(self):
        rank = 40 - self.health
        if not self.alive:
            rank += self.placing * 1000
        return rank


# ############################# Tavern ############################# #

class Tavern:
    tierUpCosts = [5, 7, 8, 9, 10]

    def __init__(self, player):
        self.player = player
        self.tier = 1
        self.tierUpCost = Tavern.tierUpCosts[0]
        self.rollCost = 1
        self.freeRolls = 0
        self.nooffers = 3
        self.minionPool = player.game.minionPool
        self.offers = self.minionPool.get_minions(self.tier, self.nooffers)

    # ############################# Tavern Actions ############################# #

    def buy(self, index):
        if self.player.gold < 3:
            self.log("Insufficient gold for buying.")
            return
        if len(self.player.hand) >= 10:
            self.log("Tried buying but hand was full.")
            return
        if not 0 <= index < len(self.offers):
            self.log("Invalid index for buying with the current board state.")
            return

        minion = self.offers.pop(index)
        self.player.gold -= 3
        self.log("Bought " + str(minion) + ".")
        self.player.try_add_to_hand(minion)
        for m in self.player.onBuy:
            self.log(str(m) + " triggers its 'after buy' effect.")
            m.on_buy(self.player, minion)

    def sell(self, index):
        if not 0 <= index < self.player.get_board_size():
            self.log("Invalid index for selling with the current board state.")
            return

        minion = self.player.get_minion(index)
        self.log("Sold " + str(minion) + ".")
        if TriggerTavern.ON_SELL in minion.triggerTavern:
            self.log(str(minion) + " triggers its 'on sell' effect.")
            minion.on_sell(self.player)
        self.minionPool.return_one(minion)
        self.player.leave_board(minion)
        self.player.gold += 1
        if self.player.gold > 10:
            self.player.gold = 10

    def tier_up(self):
        if self.tier >= 6:
            self.log("Already at tier 6.")
            return
        if self.player.gold < self.tierUpCost:
            self.log("Insufficient gold for tiering up.")
            return

        self.player.gold -= self.tierUpCost
        self.tierUpCost = Tavern.tierUpCosts[self.tier]
        self.tier += 1
        if self.nooffers < 7 and (self.tier == 2 or self.tier == 4 or self.tier == 6):
            self.nooffers += 1
        self.log("Leveled to tavern tier " + str(self.tier) + ".")

    def roll(self):
        if self.freeRolls == 0:
            if self.player.gold < self.rollCost:
                self.log("Insufficient gold for rolling.")
                return

            self.player.gold -= self.rollCost
        else:
            self.freeRolls -= 1
        self.minionPool.return_many(self.offers)
        self.offers = self.minionPool.get_minions(self.tier, self.nooffers)
        self.log("Rerolled the tavern.")

    def freeze(self):
        if any(Keyword.FROZEN not in minion.keywords for minion in self.offers):
            for m in self.offers:
                if Keyword.FROZEN not in m.keywords:
                    m.keywords.append(Keyword.FROZEN)
            self.log("Froze the tavern.")
        else:
            for m in self.offers:
                if Keyword.FROZEN in m.keywords:
                    m.keywords.remove(Keyword.FROZEN)
            self.log("Unfroze the tavern.")

    # ############################# Internal 'Happenings' ############################# #

    def start_of_turn(self):
        for m in self.offers:
            if Keyword.FROZEN in m.keywords:
                m.keywords.remove(Keyword.FROZEN)
            else:
                self.minionPool.return_one(m)
                self.offers.remove(m)
        self.offers.extend(self.minionPool.get_minions(self.tier, self.nooffers - len(self.offers)))
        if self.tierUpCost > 0:
            self.tierUpCost -= 1

    # ############################# Helpers ############################# #

    def log(self, text):
        self.player.game.log(text)

    def __str__(self):
        s = "   Tavern (Tier: " + str(self.tier) + "):\n" + "      Tier Up: " + str(self.tierUpCost) \
            + "   Roll: " + str(self.rollCost) + "   Freeze: 0\n\n"
        if len(self.offers) == 0:
            s += "      empty ¯\\_(ツ)_/¯\n"
        for m in self.offers:
            s += "      " + str(m) + "\n"
        return s
