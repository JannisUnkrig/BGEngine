import unittest

from Simulator.Game import setup_game


class TestAcolytheOfCThun(unittest.TestCase):

    def test_acolythe_of_cthun(self):
        game = setup_game(123, "acolytheOfCThun | 2/5 minion")
        game.battle(1, 0)
        self.maxDiff = None
        self.assertEqual(game.test_log,
                         "Started combat between Player 0 and Player 1.\n"
                         "2/5 Dummy Minion attacks 2/2 Acolythe of C´Thun (Taunt, Reborn).\n"
                         "2/0 Acolythe of C´Thun (Taunt, Reborn) took 2 damage.\n"
                         "2/3 Dummy Minion took 2 damage.\n"
                         "2/0 Acolythe of C´Thun (Taunt, Reborn) died.\n"
                         "2/x Acolythe of C´Thun (Taunt, Reborn) gets reborn.\n"
                         "2/x Acolythe of C´Thun (Taunt, Reborn) summoned 2/1 Acolythe of C´Thun (Taunt) at position 1.\n"
                         "2/1 Acolythe of C´Thun (Taunt) attacks 2/3 Dummy Minion.\n"
                         "2/1 Dummy Minion took 2 damage.\n"
                         "2/-1 Acolythe of C´Thun (Taunt) took 2 damage.\n"
                         "2/-1 Acolythe of C´Thun (Taunt) died.\n"
                         "Combat is over.\n"
                         "Player 1 dealt 2 damage to Player 0.\n")

    def test_golden_acolythe_of_cthun(self):
        game = setup_game(123, "4/4 golden acolytheOfCThun | 4/9 minion")
        game.battle(1, 0)
        self.maxDiff = None
        self.assertEqual(game.test_log,
                         "Started combat between Player 0 and Player 1.\n"
                         "4/9 Dummy Minion attacks 4/4 golden Acolythe of C´Thun (Taunt, Reborn).\n"
                         "4/0 golden Acolythe of C´Thun (Taunt, Reborn) took 4 damage.\n"
                         "4/5 Dummy Minion took 4 damage.\n"
                         "4/0 golden Acolythe of C´Thun (Taunt, Reborn) died.\n"
                         "4/x golden Acolythe of C´Thun (Taunt, Reborn) gets reborn.\n"
                         "4/x golden Acolythe of C´Thun (Taunt, Reborn) summoned 4/1 golden Acolythe of C´Thun (Taunt) at position 1.\n"
                         "4/1 golden Acolythe of C´Thun (Taunt) attacks 4/5 Dummy Minion.\n"
                         "4/1 Dummy Minion took 4 damage.\n"
                         "4/-3 golden Acolythe of C´Thun (Taunt) took 4 damage.\n"
                         "4/-3 golden Acolythe of C´Thun (Taunt) died.\n"
                         "Combat is over.\n"
                         "Player 1 dealt 2 damage to Player 0.\n")


if __name__ == '__main__':
    unittest.main()
