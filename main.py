from tkinter import *

from Simulator.Game import Game, setup_game
from Skynet.V1.AgentPlayerAdapterUtils import get_observation, execute_action, action_no_to_string
from Skynet.V1.Agent import IgnorantAgent


class MainFrame(Frame):

    def __init__(self):
        # Game Logic
        self.game = Game(self)
        self.doLog = True
        self.agent = None
        try:
            self.agent = IgnorantAgent("Skynet/V1/AgentModels/dqn_model_agent_0")
        except (ImportError, IOError):
            pass

        # Main Frame
        self.master = Tk()
        super().__init__(self.master)
        self.master.title("Battlegrounds Engine")
        self.master.geometry('1000x563')
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Monitor
        self.monitor = Text(master=self.master, bg='white', state=DISABLED, font=("Arial", 9), relief='flat')
        self.monitor.grid(column=0, row=0, rowspan=2, padx=5, pady=5, sticky="nesw")

        # Log
        self.log_field = Text(master=self.master, bg='white', width=60, font=("Arial", 9), relief='flat')
        self.log_field.grid(column=1, row=0, padx=5, pady=5, sticky="nesw")
        self.log_field.insert(1.0, "Start of Console:\n")
        self.log_field['state'] = DISABLED

        # Commandline
        self.commandline = Entry(master=self.master, width=60)
        self.commandline.grid(column=1, row=1, padx=5, pady=5, sticky="ew")
        self.command = StringVar()
        self.command.set("help")  # displayed on init
        self.commandline["textvariable"] = self.command
        self.commandline.bind('<Key-Return>', self.execute_commandline_input)

        self.show_active_player()

    def execute_commandline_input(self, _):
        cmd = self.command.get()
        self.command.set("")
        self.always_add_to_log(cmd, is_cmd=True)
        split = cmd.split(" ")

        if split[0] == "help":
            if len(split) != 1:
                self.always_add_to_log("\"help\" doesn't need parameters.")
                return
            self.always_add_to_log("Help:\n"
                                   "   Control Commands:\n"
                                   "      newgame: Starts a new game.\n"
                                   "      setupgame seed (args): Complex command to setup a specific game.\n"
                                   "      player x: Changes the Player you control.\n"
                                   "      startturn: Skips straight to the start of the next turn.\n"
                                   "      endturn: Triggers all \"end of turn\" events.\n"
                                   "      battle x (mode): Battle player x (mode = fast (default) / slow / debug).\n"
                                   "      step: Does a Step in debug-mode of battle.\n"
                                   "      bobsbuddy x (iter.): Finds combat outcome percentages against Player x.\n"
                                   "      combatphase: Does a full combat-phase.\n"
                                   "      timeisup: Ends this turn, does a combatphase and starts the next turn.\n"
                                   "      get x: gets you a minion (e.g. x = 1/1 golden redWhelp (taunt,plants))\n"
                                   "      history: Shows active players combat history.\n"
                                   "      standings: Shows current standings.\n"
                                   "      log x: En-/Disable logging (x = 'on'/'off').\n"
                                   "      pool: Shows what is left in the pool.\n"
                                   "   Player Commands:\n"
                                   "      play (x) (y) (z): Plays card in hand position x to board position\n"
                                   "                                y targeting z (defaults = 0).\n"
                                   "      move x y: Moves minion from position x by y to the right.\n"
                                   "      buy x: Buys the minion from shop position x.\n"
                                   "      sell (x): Sells the minion on position x (default = 0)\n"
                                   "      tierup: Levels the tavern up.\n"
                                   "      roll: Rerolls the taverns offers.\n"
                                   "      freeze: (Un-)freezes the tavern.\n"
                                   "   A.I. Commands:\n"
                                   "      agent filename: Loads an Agent from /Skynet/V1/AgentModels.\n"
                                   "      aieval x: Agent evaluates actions (x = moves left before combat).\n"
                                   "      aimove x: Agent performs one action (x = moves left before combat).\n"
                                   )

        elif split[0] == "newgame":
            if len(split) != 1:
                self.always_add_to_log("\"newgame\" doesn't need parameters.")
                return
            self.game = Game(self)
            self.always_add_to_log("Started a new game.")
            self.show_active_player()

        # setupgame 1337 3/3 alleycat (taunt) | | 4/2 golden fiendishServant (taunt,deathrattle), baronRivendare
        elif split[0] == "setupgame":
            if not 2 <= len(split) or not split[1].isnumeric():
                self.always_add_to_log("\"setupgame\" needs 1 - 2 parameters (seed and game state).")
                return
            if len(split) == 2:
                self.game = Game(self, split[1])
            else:
                args = cmd.removeprefix("setupgame " + split[1] + " ")
                self.game = setup_game(int(split[1]), args, mf=self)
            self.show_active_player()

        elif split[0] == "player":
            if len(split) != 2 or not split[1].isnumeric() or not 0 <= int(split[1]) <= 7:
                self.always_add_to_log("\"player\" needs exactly one parameter between 0 and 7.")
                return
            self.game.choose_player(int(split[1]))
            self.show_active_player()

        elif split[0] == "startturn":
            if len(split) != 1:
                self.always_add_to_log("\"startturn\" doesn't need parameters.")
                return
            self.game.start_turn()
            self.show_active_player()

        elif split[0] == "endturn":
            if len(split) != 1:
                self.always_add_to_log("\"endturn\" doesn't need parameters.")
                return
            self.game.end_turn()
            self.show_active_player()

        elif split[0] == "battle":
            if not 2 <= len(split) <= 3:
                self.always_add_to_log("\"battle\" command needs 1 or 2 parameters.")
                return
            if not split[1].isnumeric() or not 0 <= int(split[1]) <= 7:
                self.always_add_to_log("First parameter should be the opponents player number (0-7).")
                return
            if len(split) == 3 and split[2] != "fast" and split[2] != "slow" and split[2] != "debug":
                self.always_add_to_log("Second optional parameter should be the mode ('fast', 'slow' or 'debug').")
                return
            if len(split) == 2:
                self.game.battle(int(split[1]))
            else:
                self.game.battle(int(split[1]), mode=split[2])
            if len(split) != 3 or split[2] != "debug":
                self.show_active_player()

        elif split[0] == "step":
            if self.game.curCombat is None:
                self.always_add_to_log("No combat is happening right now.")
                return
            if len(split) != 1:
                self.always_add_to_log("\"step\" doesn't need parameters.")
                return
            self.game.step()
            if self.game.curCombat is not None:
                self.show_on_monitor(str(self.game.curCombat))
            else:
                self.show_active_player()

        elif split[0] == "bobsbuddy":
            if not 2 <= len(split) <= 3:
                self.always_add_to_log("\"bobsbuddy\" command needs 1 or 2 parameters.")
                return
            if not split[1].isnumeric() or not 0 <= int(split[1]) <= 7:
                self.always_add_to_log("First parameter should be the opponents player number (0-7).")
                return
            if len(split) == 3 and not split[2].isnumeric():
                self.always_add_to_log("Second optional parameter should be the number of iterations.")
                return
            if len(split) == 2:
                self.game.bobs_buddy(int(split[1]))
            else:
                self.game.bobs_buddy(int(split[1]), iterations=int(split[2]))

        elif split[0] == "combatphase":
            if len(split) != 1:
                self.always_add_to_log("\"combatphase\" doesn't need parameters.")
                return
            self.game.combat_phase()
            self.show_active_player()

        elif split[0] == "timeisup":
            if len(split) != 1:
                self.always_add_to_log("\"timeisup\" doesn't need parameters.")
                return
            self.game.time_is_up()
            self.show_active_player()

        elif split[0] == "get":
            if not len(split) >= 2:
                self.always_add_to_log("\"get\" needs 1 parameter.")
                return
            args = cmd.removeprefix("get ")
            self.game.cheat_in_minion(args)
            self.show_active_player()

        elif split[0] == "history":
            if len(split) != 1:
                self.always_add_to_log("\"history\" doesn't need parameters.")
                return
            self.always_add_to_log(self.game.activePlayer.get_history())

        elif split[0] == "standings":
            if len(split) != 1:
                self.always_add_to_log("\"standings\" doesn't need parameters.")
                return
            self.always_add_to_log(self.game.get_standings())

        elif split[0] == "log":
            if not 1 <= len(split) <= 2:
                self.always_add_to_log("\"log\" needs 0 or 1 parameters.")
                return
            if len(split) == 1:
                if self.doLog:
                    self.always_add_to_log("Logging is enabled.")
                else:
                    self.always_add_to_log("Logging is disabled.")
            else:
                if split[1] == "on":
                    self.doLog = True
                    self.always_add_to_log("Logging enabled.")
                elif split[1] == "off":
                    self.doLog = False
                    self.always_add_to_log("Logging disabled.")
                else:
                    self.always_add_to_log("Argument of \"log\" can be None, 'on' or 'off'.")

        elif split[0] == "pool":
            if len(split) != 1:
                self.always_add_to_log("\"pool\" doesn't need parameters.")
                return
            self.always_add_to_log(str(self.game.minionPool))

        # ############################# Active Players Commands ############################# #

        elif split[0] == "play":
            if not 1 <= len(split) <= 4:
                self.always_add_to_log("\"play\" needs 0-3 parameters.")
                return
            if len(split) >= 2 and (not split[1].isnumeric() or not 0 <= int(split[1]) <= 9):
                self.always_add_to_log("First parameter should be the cards index in hand (0-9).")
                return
            if len(split) >= 3 and (not split[2].isnumeric() or not 0 <= int(split[2]) <= 6):
                self.always_add_to_log("Second parameter should be the cards destination index (0-6).")
                return
            if len(split) == 4 and (not split[3].isnumeric() or not 0 <= int(split[3]) <= 6):
                self.always_add_to_log("Third parameter should be the battlecry targets index (0-6).")
                return
            if len(split) == 1:
                self.game.activePlayer.play()
            elif len(split) == 2:
                self.game.activePlayer.play(int(split[1]))
            elif len(split) == 3:
                self.game.activePlayer.play(int(split[1]), int(split[2]))
            else:
                self.game.activePlayer.play(int(split[1]), int(split[2]), int(split[3]))
            self.show_active_player()

        elif split[0] == "move":
            if not len(split) == 3 or not split[1].isnumeric() or not 0 <= int(split[1]) <= 6 \
                    or not split[2].lstrip('-').isnumeric() or not -6 <= int(split[2]) <= 6:
                self.always_add_to_log("\"move\" needs exactly 2 parameters (0-6 and (-6)-6).")
                return
            self.game.activePlayer.move(int(split[1]), int(split[2]))
            self.show_active_player()

        elif split[0] == "buy":
            if len(split) != 2 or not split[1].isnumeric() or not 0 <= int(split[1]) <= 6:
                self.always_add_to_log("\"buy\" needs exactly one parameter between 0 and 6.")
                return
            self.game.activePlayer.buy(int(split[1]))
            self.show_active_player()

        elif split[0] == "sell":
            if len(split) != 2 or not split[1].isnumeric() or not 0 <= int(split[1]) <= 6:
                self.always_add_to_log("\"sell\" needs exactly one parameter between 0 and 6.")
                return
            self.game.activePlayer.sell(int(split[1]))
            self.show_active_player()

        elif split[0] == "tierup":
            if len(split) != 1:
                self.always_add_to_log("\"tierup\" doesn't need parameters.")
                return
            self.game.activePlayer.tier_up()
            self.show_active_player()

        elif split[0] == "roll":
            if len(split) != 1:
                self.always_add_to_log("\"roll\" doesn't need parameters.")
                return
            self.game.activePlayer.roll()
            self.show_active_player()

        elif split[0] == "freeze":
            if len(split) != 1:
                self.always_add_to_log("\"freeze\" doesn't need parameters.")
                return
            self.game.activePlayer.freeze()
            self.show_active_player()

        elif split[0] == "choose":
            if len(split) != 2 or not split[1].isnumeric():
                self.always_add_to_log("\"choose\" needs exactly one parameter (index of the choice).")
                return
            self.game.activePlayer.choose(int(split[1]))
            self.show_active_player()

        # ############################# A.I. Commands ############################# #

        elif split[0] == "agent":
            if len(split) != 2:
                self.always_add_to_log("\"agent\" needs exactly 1 parameter (filename).")
                return
            try:
                self.agent = IgnorantAgent("Skynet/V1/AgentModels/" + split[1])
                self.always_add_to_log("Loaded " + split[1] + " from /Skynet/V1/AgentModels.")
            except (ImportError, IOError):
                self.always_add_to_log("No file with name \"" + split[1] + "\" found in /Skynet/V1/AgentModels.")

        elif split[0] == "aieval":
            if len(split) != 2 or not split[1].isnumeric():
                self.always_add_to_log("\"aieval\" needs exactly 1 parameter (moves left until combat).")
                return
            observation = get_observation(int(split[1]), self.game.activePlayer)
            action_qualities = self.agent.evaluate_actions(observation)
            self.always_add_to_log(action_no_to_string(action_qualities))

        elif split[0] == "aimove":
            if len(split) != 2 or not split[1].isnumeric():
                self.always_add_to_log("\"aimove\" needs exactly 1 parameter (moves left until combat).")
                return
            observation = get_observation(int(split[1]), self.game.activePlayer)
            action_no = self.agent.choose_action(observation)
            execute_action(self.game.activePlayer, action_no)
            self.show_active_player()

        else:
            self.always_add_to_log("Invalid command.")

    def show_on_monitor(self, text):
        self.monitor['state'] = NORMAL
        self.monitor.delete(1.0, END)
        self.monitor.insert(1.0, text)
        self.monitor['state'] = DISABLED
        self.master.update_idletasks()

    def show_active_player(self):
        self.show_on_monitor(str(self.game.activePlayer))

    def log(self, text):
        if self.doLog:
            self.always_add_to_log(text)

    def always_add_to_log(self, text, is_cmd=False):
        self.log_field['state'] = NORMAL
        if is_cmd:
            self.log_field.insert(END, "> " + text + "\n")
        else:
            self.log_field.insert(END, text + "\n")
        self.log_field['state'] = DISABLED


mf = MainFrame()
mf.mainloop()
