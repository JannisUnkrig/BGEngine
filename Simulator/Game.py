import random

from Simulator.Combat import Combat
from Simulator.MinionPool import MinionPool, minion_from_advanced_string
from Simulator.PlayerAndTavern import Player


class Game:

    def __init__(self, mf=None, seed=None):
        self.mf = mf
        if seed is not None:
            random.seed(seed)
        self.test_log = ""

        self.turn = 1
        self.minionPool = MinionPool()
        self.players = [Player(self) for _ in range(8)]
        for i in range(8):
            self.players[i].playerNo = i
        self.playersRemaining = 8
        self.over = False

        self.activePlayer = self.players[0]
        self.curCombat = None

    def choose_player(self, player_no):
        self.activePlayer = self.players[player_no]
        self.log("You're now playing as Player " + str(player_no) + ".")

    def start_turn(self):
        for p in self.players:
            p.start_of_turn()
        self.turn += 1
        self.log("Turn " + str(self.turn) + " started.")

    def end_turn(self):
        for p in self.players:
            p.end_of_turn()
        self.log("Turn " + str(self.turn) + " ended.")

    def battle(self, enemy_player_no, own_player_no=-1, mode="fast"):
        if own_player_no == -1:
            own_player_no = self.activePlayer.playerNo
        self.curCombat = Combat(self.players[own_player_no], self.players[enemy_player_no], self)
        self.curCombat.start(mode)

    def step(self):
        if self.curCombat is not None:
            self.curCombat.step()

    def bobs_buddy(self, enemy_player_no, own_player_no=-1, iterations=1000):
        if own_player_no == -1:
            own_player_no = self.activePlayer.playerNo
        own_player = self.players[own_player_no]
        enemy_player = self.players[enemy_player_no]

        wins = 0
        ties = 0
        losses = 0

        tmpDoLog = None
        if self.mf is not None:
            tmpDoLog = self.mf.doLog
            self.mf.doLog = False

        for i in range(iterations):
            c = Combat(own_player, enemy_player, self, has_consequences=False)
            c.start()
            if c.damage_dealt_or_taken > 0:
                wins += 1
            elif c.damage_dealt_or_taken == 0:
                ties += 1
            else:
                losses += 1

        if self.mf is not None:
            self.mf.doLog = tmpDoLog

        self.log("Win: " + str(wins / iterations * 100) +
                 "% Tie: " + str(ties / iterations * 100) +
                 "% Loss: " + str(losses / iterations * 100) + "%")

    def combat_phase(self):
        self.log("Starting combat phase.")
        alive_players = list(filter(lambda p2: p2.alive, self.players))

        # if ood number left -> find ghost
        ghost = None
        if len(alive_players) % 2 == 1:
            cur_highest_placing = 9
            for p in self.players:
                if not p.alive and p.placing < cur_highest_placing:
                    cur_highest_placing = p.placing
                    ghost = p
            alive_players.append(ghost)

        # only two players left
        if len(alive_players) == 2:
            Combat(alive_players[0], alive_players[1], self).start()
            return

        # atleast 3 players + ghost left
        while True:
            combats = []
            to_match = alive_players.copy()
            if ghost is not None:
                to_match.remove(ghost)
                to_match.sort(key=lambda p2: p2.health)
                low_enough_health = to_match[:3]
                disqualified = ghost.enemy_history[-2:]
                valid_ghost_enemies = list(filter(lambda player: player not in disqualified, low_enough_health))
                ghost_enemy = random.choice(valid_ghost_enemies)
                to_match.remove(ghost_enemy)
                combats.append(Combat(ghost_enemy, ghost, self))
            while len(to_match) > 0:
                p = to_match[0]
                to_match.remove(p)
                disqualified = p.enemy_history[-2:]
                valid_enemies = list(filter(lambda player: player not in disqualified, to_match))
                if len(valid_enemies) == 0:
                    print("invalid pairing")
                    continue
                enemy = random.choice(valid_enemies)
                to_match.remove(enemy)
                combats.append(Combat(p, enemy, self))

            for c in combats:
                c.start()
            return

    def time_is_up(self):
        self.end_turn()
        self.combat_phase()
        self.start_turn()

    def cheat_in_minion(self, minion_name, player_no=-1):
        if player_no == -1:
            p = self.activePlayer
        else:
            p = self.players[player_no]

        m = minion_from_advanced_string(minion_name)
        if m is None:
            self.log("Invalid minion name")
            return
        self.log("Added " + str(m) + " to Player " + str(p.playerNo) + "s hand.")
        p.try_add_to_hand(m)

    def get_standings(self):
        ranking = sorted(self.players, key=lambda p: p.sorting_func())
        s = ""
        for player in ranking:
            if player.placing > 0:
                s += str(player.placing) + ". "
            s += "Player " + str(player.playerNo) + " (" + str(player.health) + " Health)\n"
        return s

    def log(self, text):
        if self.mf is None:
            self.test_log += text + "\n"
        else:
            self.mf.log(text)

    # use sparingly. display updates should be done in m if possible
    def disp(self, text):
        if self.mf is not None:
            self.mf.show_on_monitor(text)


# spec should look like:
# 3/3 alleycat (taunt), 4/2 acolytheOfCThun | | 4/2 golden fiendishServant (taunt,divineshield), baronRivendare
# (player 1 has no minions in this example)
# NO SPACES IN THE KEYWORD LIST
def setup_game(seed, spec, mf=None):
    game = Game(seed=seed)
    ps = spec.split("|")
    for i, p in enumerate(ps):
        p = p.strip()
        if p == "":
            continue

        ms = p.split(", ")
        for m in ms:
            minion = minion_from_advanced_string(m)
            if minion is None:
                if mf is not None:
                    mf.always_add_to_log("Error in specification of minion: " + m + ".\nOnly the seed will be used.")
                return Game(mf, seed)
            game.players[i].appear_on_board(minion)

    if mf is not None:
        mf.always_add_to_log("Set specified game up.")
    return game
