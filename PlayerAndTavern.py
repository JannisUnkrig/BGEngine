import copy
from Minions import Keyword, TriggerTavern, get_from_pool, return_one_to_pool, return_many_to_pool


# ############################# Player ############################# #

class Player:
    noOfPlayers = 0

    def __init__(self):
        self.playerNo = Player.noOfPlayers
        Player.noOfPlayers += 1
        self._health = 40
        self.maxGold = 3
        self.gold = 3
        self.hand = []
        self._board = []
        self.tavern = Tavern(self)
        self.matchHistory = {}  # TODO

        self._onPlay = []               # minion.on_play(self, minion, position)
        self.validBcTarget = True
        self._afterPlay = []            # minion.after_play(self, minion)
        self._onSummon = []             # minion.on_summon(self, summoners, summoned)
        self.afterBuy = []              # minion.after_buy(self, minion)
        self.onSell = []                # minion.on_sell(self, minion)
        self._onStartOfTurn = []        # minion.on_start_of_turn(self)
        self._onEndOfTurn = []          # minion.on_end_of_turn(self)
        self._onTakeHeroDamage = []     # minion.on_take_hero_damage(self)

    # ############################# Player Actions ############################# #

    def play(self, from_index=0, to_index=0, bc_target=0):
        if not 0 <= from_index < len(self.hand) \
                or not 0 <= to_index <= len(self._board) \
                or not 0 <= bc_target < max(1, len(self._board)):
            return "Invalid indexes for the current board state."

        minion = self.hand[from_index]

        if Keyword.BATTLECRY in minion.keywords:
            self.validBcTarget = True
            minion.battlecry(self, to_index, bc_target)
            if not self.validBcTarget:
                return "Invalid target for battlecry."

        for m in self._onPlay:
            m.on_play(self, minion, to_index, bc_target)

        self.hand.remove(minion)
        self._board.insert(to_index, minion)

        for m in self._afterPlay:
            m.after_play(self, minion)

        self.add_to_trigger_list(minion)
        return "Played " + str(minion) + " to position " + str(to_index) + "."

    def move(self, pos, by):
        if not 0 <= pos < len(self._board) or not 0 <= pos + by < len(self._board):
            return "Invalid indexes for the current board state."
        tmp = self._board.pop(pos)
        self._board.insert(pos + by, tmp)
        return "Moved " + str(tmp) + " " + str(by) + " to the right"

    def buy(self, index):
        return self.tavern.buy(index)

    def sell(self, index):
        return self.tavern.sell(index)

    def tier_up(self):
        return self.tavern.tier_up()

    def roll(self):
        return self.tavern.roll()

    def freeze(self):
        return self.tavern.freeze()

    # ############################# Internal 'Happenings' ############################# #

    def leave_board(self, minion):
        self.remove_from_trigger_list(minion)
        self._board.remove(minion)

    def summon(self, summoners, summoned, position):
        if len(self._board) >= 7:
            return
        self.add_to_trigger_list(summoned)
        for m in self._onSummon:
            m.on_summon(self, summoners, summoned)
        self._board.insert(position, summoned)

    def take_hero_damage(self, how_much):
        for m in self._onTakeHeroDamage:
            m.on_take_hero_damage(self)
        self._health -= how_much

    def start_of_turn(self):
        for m in self._onStartOfTurn:
            m.on_start_of_turn(self)
        if self.maxGold < 10:
            self.maxGold += 1
        self.gold = self.maxGold
        self.tavern.start_of_turn()

    def end_of_turn(self):
        for m in self._onEndOfTurn:
            m.on_end_of_turn(self)

    # ############################# Helpers ############################# #

    def get_board_copy(self):
        return copy.deepcopy(self._board)

    def get_board_size(self):
        return len(self._board)

    def get_minion(self, index):
        return self._board[index]

    def add_to_trigger_list(self, minion):
        if TriggerTavern.ON_PLAY in minion.triggerTavern:
            self._onPlay.append(minion)
        if TriggerTavern.AFTER_PLAY in minion.triggerTavern:
            self._afterPlay.append(minion)
        if TriggerTavern.ON_SUMMON in minion.triggerTavern:
            self._onSummon.append(minion)
        if TriggerTavern.AFTER_BUY in minion.triggerTavern:
            self.afterBuy.append(minion)
        if TriggerTavern.ON_SELL in minion.triggerTavern:
            self.onSell.append(minion)
        if TriggerTavern.ON_START_OF_TURN in minion.triggerTavern:
            self._onStartOfTurn.append(minion)
        if TriggerTavern.ON_END_OF_TURN in minion.triggerTavern:
            self._onEndOfTurn.append(minion)
        if TriggerTavern.ON_TAKE_HERO_DAMAGE in minion.triggerTavern:
            self._onTakeHeroDamage.append(minion)

    def remove_from_trigger_list(self, minion):
        if TriggerTavern.ON_PLAY in minion.triggerTavern:
            self._onPlay.remove(minion)
        if TriggerTavern.AFTER_PLAY in minion.triggerTavern:
            self._afterPlay.remove(minion)
        if TriggerTavern.ON_SUMMON in minion.triggerTavern:
            self._onSummon.remove(minion)
        if TriggerTavern.AFTER_BUY in minion.triggerTavern:
            self.afterBuy.remove(minion)
        if TriggerTavern.ON_SELL in minion.triggerTavern:
            self.onSell.remove(minion)
        if TriggerTavern.ON_START_OF_TURN in minion.triggerTavern:
            self._onStartOfTurn.remove(minion)
        if TriggerTavern.ON_END_OF_TURN in minion.triggerTavern:
            self._onEndOfTurn.remove(minion)
        if TriggerTavern.ON_TAKE_HERO_DAMAGE in minion.triggerTavern:
            self._onTakeHeroDamage.remove(minion)

    def __str__(self):
        s = "Player " + str(self.playerNo) + ":\n   Gold: " + str(self.gold) + "/" + str(self.maxGold) + "   Health: " \
            + str(self._health) + "\n\n" + str(self.tavern) + "\n   Board:\n"
        if len(self._board) == 0:
            s += "      empty ¯\\_(ツ)_/¯\n"
        for m in self._board:
            s += "      " + str(m) + "\n"
        s += "\n   Hand:\n"
        if len(self.hand) == 0:
            s += "      empty ¯\\_(ツ)_/¯\n"
        for m in self.hand:
            s += "      " + str(m) + "\n"
        return s


# ############################# Tavern ############################# #

class Tavern:

    levelUpCosts = [5, 7, 8, 9, 10]

    def __init__(self, player):
        self.player = player
        self.tier = 1
        self.tierUpCost = Tavern.levelUpCosts[0]
        self.rollCost = 1
        self.nooffers = 3
        self.offers = get_from_pool(self.tier, self.nooffers)

    # ############################# Tavern Actions ############################# #

    def buy(self, index):
        if self.player.gold < 3:
            return "Insufficient gold."
        if not 0 <= index < len(self.offers):
            return "Invalid index for the current board state."

        minion = self.offers.pop(index)
        self.player.hand.append(minion)
        self.player.gold -= 3
        for m in self.player.afterBuy:
            m.afterBuy(self.player, minion)
        return "Bought " + str(minion) + "."

    def sell(self, index):
        if not 0 <= index < self.player.get_board_size():
            return "Invalid index for the current board state."

        minion = self.player.get_minion(index)
        for m in self.player.onSell:
            m.onSell(self.player, minion)
        return_one_to_pool(minion)
        self.player.leave_board(minion)
        self.player.gold += 1
        if self.player.gold > 10:
            self.player.gold = 10
        return "Sold " + str(minion) + "."

    def tier_up(self):
        if self.tier >= 6:
            return "Already at tier 6."
        if self.player.gold < self.tierUpCost:
            return "Insufficient gold."

        self.player.gold -= self.tierUpCost
        self.tierUpCost = Tavern.levelUpCosts[self.tier]
        self.tier += 1
        if self.nooffers < 7 and (self.tier == 2 or self.tier == 4 or self.tier == 6):
            self.nooffers += 1
        return "Leveled to tavern tier " + str(self.tier) + "."

    def roll(self):
        if self.player.gold < self.rollCost:
            return "Insufficient gold."

        return_many_to_pool(self.offers)
        self.offers = get_from_pool(self.tier, self.nooffers)
        self.player.gold -= self.rollCost
        return "Rerolled the tavern."

    def freeze(self):
        if any(Keyword.FROZEN not in minion.keywords for minion in self.offers):
            for m in self.offers:
                if Keyword.FROZEN not in m.keywords:
                    m.keywords.append(Keyword.FROZEN)
            return "Froze the tavern."
        else:
            for m in self.offers:
                if Keyword.FROZEN in m.keywords:
                    m.keywords.remove(Keyword.FROZEN)
            return "Unfroze the tavern."

    # ############################# Internal 'Happenings' ############################# #

    def start_of_turn(self):
        for m in self.offers[:]:
            if Keyword.FROZEN in m.keywords:
                m.keywords.remove(Keyword.FROZEN)
            else:
                return_one_to_pool(m)
                self.offers.remove(m)
        self.offers.extend(get_from_pool(self.tier, self.nooffers - len(self.offers)))
        if self.tierUpCost > 0:
            self.tierUpCost -= 1

    # ############################# Helpers ############################# #

    def __str__(self):
        s = "   Tavern (Tier: " + str(self.tier) + "):\n" + "      Tier Up: " + str(self.tierUpCost)\
            + "   Roll: " + str(self.rollCost) + "   Freeze: 0\n\n"
        if len(self.offers) == 0:
            s += "      empty ¯\\_(ツ)_/¯\n"
        for m in self.offers:
            s += "      " + str(m) + "\n"
        return s
