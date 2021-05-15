import unittest

from Simulator.Game import setup_game


class TestFiendishServant(unittest.TestCase):

    def test_fiendish_servant(self):
        game = setup_game(123, "fiendishServant, minion | minion (taunt)")
        game.battle(1, 0)
        self.maxDiff = None
        self.assertEqual(game.test_log,
                         "Started combat between Player 0 and Player 1.\n"
                         "2/1 Fiendish Servant (Deathrattle) attacks 1/1 Dummy Minion (Taunt).\n"
                         "1/-1 Dummy Minion (Taunt) took 2 damage.\n"
                         "2/0 Fiendish Servant (Deathrattle) took 1 damage.\n"
                         "2/0 Fiendish Servant (Deathrattle) died.\n"
                         "1/-1 Dummy Minion (Taunt) died.\n"
                         "2/x Fiendish Servant (Deathrattle) triggers its deathrattle effect.\n"
                         "Buffed 3/1 Dummy Minion with (2/0).\n"
                         "Combat is over.\n"
                         "Player 0 dealt 2 damage to Player 1.\n")

    def test_fiendish_servant_no_target(self):
        game = setup_game(124, "fiendishServant | minion")
        game.battle(1, 0)
        self.maxDiff = None
        self.assertEqual(game.test_log,
                         "Started combat between Player 0 and Player 1.\n"
                         "2/1 Fiendish Servant (Deathrattle) attacks 1/1 Dummy Minion.\n"
                         "1/-1 Dummy Minion took 2 damage.\n"
                         "2/0 Fiendish Servant (Deathrattle) took 1 damage.\n"
                         "1/-1 Dummy Minion died.\n"
                         "2/0 Fiendish Servant (Deathrattle) died.\n"
                         "2/x Fiendish Servant (Deathrattle) triggers its deathrattle effect.\n"
                         "Combat is over.\n"
                         "Player 0 and Player 1 tied.\n")

    def test_golden_fiendish_servant(self):
        game = setup_game(123, "4/2 golden fiendishServant, minion | 2/2 minion")
        game.battle(1, 0)
        self.maxDiff = None
        self.assertEqual(game.test_log,
                         "Started combat between Player 0 and Player 1.\n"
                         "4/2 golden Fiendish Servant (Deathrattle) attacks 2/2 Dummy Minion.\n"
                         "2/-2 Dummy Minion took 4 damage.\n"
                         "4/0 golden Fiendish Servant (Deathrattle) took 2 damage.\n"
                         "4/0 golden Fiendish Servant (Deathrattle) died.\n"
                         "2/-2 Dummy Minion died.\n"
                         "4/x golden Fiendish Servant (Deathrattle) triggers its deathrattle effect.\n"
                         "Buffed 5/1 Dummy Minion with (4/0).\n"
                         "Buffed 9/1 Dummy Minion with (4/0).\n"
                         "Combat is over.\n"
                         "Player 0 dealt 2 damage to Player 1.\n")


if __name__ == '__main__':
    unittest.main()
