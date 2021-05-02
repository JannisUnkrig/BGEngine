from PlayerAndTavern import Player
from Minions import pool_as_string
from Arena import Arena
from tkinter import *


class MainFrame(Frame):

    def __init__(self):
        # Game Logic
        self.turn = 1
        self.players = [Player() for _ in range(8)]
        self.activePlayer = self.players[0]
        self.arena = Arena(self)

        # Main Frame
        self.master = Tk()
        super().__init__(self.master)
        self.master.title("Battlegrounds Engine")
        self.master.geometry('850x500')
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Monitor
        self.monitor = Text(master=self.master, bg='white', state=DISABLED, font=("Arial", 9), relief='flat')
        self.monitor.grid(column=0, row=0, rowspan=2, padx=5, pady=5, sticky="nesw")

        # Log
        self.log = Text(master=self.master, bg='white', width=50, font=("Arial", 9), relief='flat')
        self.log.grid(column=1, row=0, padx=5, pady=5, sticky="nesw")
        self.log.insert(1.0, "Start of Console:\n")
        self.log['state'] = DISABLED

        # Commandline
        self.commandline = Entry(master=self.master, width=50)
        self.commandline.grid(column=1, row=1, padx=5, pady=5, sticky="ew")
        self.command = StringVar()
        self.command.set("help")
        self.commandline["textvariable"] = self.command
        self.commandline.bind('<Key-Return>', self.execute_commandline_input)

        self.show_on_monitor(str(self.activePlayer))

    def execute_commandline_input(self, _):
        cmd = self.command.get()
        self.command.set("")
        self.add_to_log(cmd, True)
        split = cmd.split(" ")

        if split[0] == "help":
            if len(split) != 1:
                self.add_to_log("\"help\" doesn't need parameters.")
                return
            self.add_to_log("Help:\n"
                            "   Control Commands:\n"
                            "      player x: Changes the Player you control.\n"
                            "      nextturn: Ends this turn and starts the next without combat.\n"
                            "      battle x (mode): Battle player x. Possible modes are: 'fast'\n"
                            "                                   (default), 'slow' and 'debug'. 'slow' and\n"
                            "                                   'debug' implicitly turn on combat logging.\n"
                            "      step: Does a Step in debug-mode of battle.\n"
                            "      combatphase: Does a full combat-phase. WIP\n"
                            "      log x: En-/Disable combat logging (x = 'on'/'off').\n"
                            "      pool: Shows what is left in the pool.\n"
                            "   Player Commands:\n"
                            "      play (x) (y) (z): Plays card in hand position x to board position\n"
                            "                                y targeting z (defaults = 0).\n"
                            "      move x y: Moves minion from position x by y to the right.\n"
                            "      buy x: Buys the minion from shop position x.\n"
                            "      sell (x): Sells the minion on position x (default = 0)\n"
                            "      tierup: Levels the tavern up.\n"
                            "      roll: Rerolls the taverns offers.\n"
                            "      freeze: (Un-)freezes the tavern.")

        elif split[0] == "player":
            if len(split) != 2 or not split[1].isnumeric() or not 0 <= int(split[1]) <= 7:
                self.add_to_log("\"player\" needs exactly one parameter between 0 and 7.")
                return
            self.activePlayer = self.players[int(split[1])]
            self.add_to_log("You're now playing as player " + split[1] + ".")
            self.show_on_monitor(str(self.activePlayer))

        elif split[0] == "nextturn":
            if len(split) != 1:
                self.add_to_log("\"nextturn\" doesn't need parameters.")
                return
            for p in self.players:
                p.end_of_turn()
                p.start_of_turn()
            self.turn += 1
            self.add_to_log("Turn " + str(self.turn) + " started.")
            self.show_on_monitor(str(self.activePlayer))

        elif split[0] == "battle":
            if not 2 <= len(split) <= 3:
                self.add_to_log("\"battle\" command needs 1 or 2 parameters.")
                return
            if not split[1].isnumeric() or not 0 <= int(split[1]) <= 7:
                self.add_to_log("First parameter should be the opponents player number (0-7).")
                return
            if len(split) == 3 and split[2] != "fast" and split[2] != "slow" and split[2] != "debug":
                self.add_to_log("Second optional parameter should be the mode ('fast', 'slow' or 'debug').")
                return
            if len(split) == 2:
                self.arena.battle(self.activePlayer, self.players[int(split[1])])
            else:
                self.arena.battle(self.activePlayer, self.players[int(split[1])], split[2])
            if len(split) < 3 or split[2] != "debug":
                self.show_on_monitor(str(self.activePlayer))

        elif split[0] == "step":
            if len(split) != 1:
                self.add_to_log("\"step\" doesn't need parameters.")
                return
            self.arena.step()

        elif split[0] == "combatphase":
            if len(split) != 1:
                self.add_to_log("\"combatphase\" doesn't need parameters.")
                return
            self.arena.combatphase(self.players)
            self.show_on_monitor(str(self.activePlayer))

        elif split[0] == "log":
            if not 1 <= len(split) <= 2:
                self.add_to_log("\"log\" needs 0 or 1 parameters.")
                return
            if len(split) == 1:
                self.add_to_log("Combat gets logged: " + str(self.arena.doLog))
            else:
                if split[1] == "on":
                    self.arena.doLog = True
                    self.add_to_log("Combat gets logged.")
                elif split[1] == "off":
                    self.arena.doLog = False
                    self.add_to_log("Combat doesn't get logged.")
                else:
                    self.add_to_log("Argument of \"log\" can be 'on' or 'off'.")

        elif split[0] == "pool":
            if len(split) != 1:
                self.add_to_log("\"pool\" doesn't need parameters.")
                return
            self.add_to_log(pool_as_string())

        elif split[0] == "play":
            if not 1 <= len(split) <= 4:
                self.add_to_log("\"play\" needs 0-3 parameters.")
                return
            if len(split) >= 2 and (not split[1].isnumeric() or not 0 <= int(split[1]) <= 9):
                self.add_to_log("First parameter should be the cards index in hand (0-9).")
                return
            if len(split) >= 3 and (not split[2].isnumeric() or not 0 <= int(split[2]) <= 6):
                self.add_to_log("Second parameter should be the cards destination index (0-6).")
                return
            if len(split) == 4 and (not split[3].isnumeric() or not 0 <= int(split[3]) <= 6):
                self.add_to_log("Third parameter should be the battlecry targets index (0-6).")
                return
            if len(split) == 1:
                response = self.activePlayer.play()
            elif len(split) == 2:
                response = self.activePlayer.play(int(split[1]))
            elif len(split) == 3:
                response = self.activePlayer.play(int(split[1]), int(split[2]))
            else:
                response = self.activePlayer.play(int(split[1]), int(split[2]), int(split[3]))
            self.add_to_log(response)
            self.show_on_monitor(str(self.activePlayer))

        elif split[0] == "move":
            if not len(split) == 3 or not split[1].isnumeric() or not 0 <= int(split[1]) <= 6 \
                    or not split[2].lstrip('-').isnumeric() or not -6 <= int(split[2]) <= 6:
                self.add_to_log("\"move\" needs exactly 2 parameters (0-6 and (-6)-6).")
                return
            self.add_to_log(self.activePlayer.move(int(split[1]), int(split[2])))
            self.show_on_monitor(str(self.activePlayer))

        elif split[0] == "buy":
            if len(split) != 2 or not split[1].isnumeric() or not 0 <= int(split[1]) <= 6:
                self.add_to_log("\"buy\" needs exactly one parameter between 0 and 6.")
                return
            self.add_to_log(self.activePlayer.buy(int(split[1])))
            self.show_on_monitor(str(self.activePlayer))

        elif split[0] == "sell":
            if len(split) != 2 or not split[1].isnumeric() or not 0 <= int(split[1]) <= 6:
                self.add_to_log("\"sell\" needs exactly one parameter between 0 and 6.")
                return
            self.add_to_log(self.activePlayer.sell(int(split[1])))
            self.show_on_monitor(str(self.activePlayer))

        elif split[0] == "tierup":
            if len(split) != 1:
                self.add_to_log("\"tierup\" doesn't need parameters.")
                return
            self.add_to_log(self.activePlayer.tier_up())
            self.show_on_monitor(str(self.activePlayer))

        elif split[0] == "roll":
            if len(split) != 1:
                self.add_to_log("\"roll\" doesn't need parameters.")
                return
            self.add_to_log(self.activePlayer.roll())
            self.show_on_monitor(str(self.activePlayer))

        elif split[0] == "freeze":
            if len(split) != 1:
                self.add_to_log("\"freeze\" doesn't need parameters.")
                return
            self.add_to_log(self.activePlayer.freeze())
            self.show_on_monitor(str(self.activePlayer))

        else:
            self.add_to_log("Invalid command.")

    def show_on_monitor(self, text):
        self.monitor['state'] = NORMAL
        self.monitor.delete(1.0, END)
        self.monitor.insert(1.0, text)
        self.monitor['state'] = DISABLED
        self.master.update_idletasks()

    def add_to_log(self, text, is_cmd=False):
        self.log['state'] = NORMAL
        if is_cmd:
            self.log.insert(END, "> " + text + "\n")
        else:
            self.log.insert(END, text + "\n")
        self.log['state'] = DISABLED


mf = MainFrame()
mf.mainloop()
