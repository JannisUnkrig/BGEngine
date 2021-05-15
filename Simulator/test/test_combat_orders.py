import unittest

from Simulator.Game import setup_game


class TestCombatOrders(unittest.TestCase):

    def test_attack_order(self):
        game = setup_game(123, "1/199 minion, 1/299 minion, 1/399 minion, 1/499 minion, 1/599 minion, 1/699 minion | "
                               "1/1 minion, 2/1 minion, 3/1 minion, 4/1 minion, 5/1 minion, 6/1 minion, 7/1 minion")
        game.battle(1, 0)
        self.maxDiff = None
        self.assertEqual(game.test_log,
                         "Started combat between Player 0 and Player 1.\n"
                         "1/1 Dummy Minion attacks 1/199 Dummy Minion.\n"
                         "1/198 Dummy Minion took 1 damage.\n"
                         "1/0 Dummy Minion took 1 damage.\n"
                         "1/0 Dummy Minion died.\n"
                         "1/198 Dummy Minion attacks 3/1 Dummy Minion.\n"
                         "3/0 Dummy Minion took 1 damage.\n"
                         "1/195 Dummy Minion took 3 damage.\n"
                         "3/0 Dummy Minion died.\n"
                         "2/1 Dummy Minion attacks 1/195 Dummy Minion.\n"
                         "1/193 Dummy Minion took 2 damage.\n"
                         "2/0 Dummy Minion took 1 damage.\n"
                         "2/0 Dummy Minion died.\n"
                         "1/299 Dummy Minion attacks 7/1 Dummy Minion.\n"
                         "7/0 Dummy Minion took 1 damage.\n"
                         "1/292 Dummy Minion took 7 damage.\n"
                         "7/0 Dummy Minion died.\n"
                         "4/1 Dummy Minion attacks 1/399 Dummy Minion.\n"
                         "1/395 Dummy Minion took 4 damage.\n"
                         "4/0 Dummy Minion took 1 damage.\n"
                         "4/0 Dummy Minion died.\n"
                         "1/395 Dummy Minion attacks 5/1 Dummy Minion.\n"
                         "5/0 Dummy Minion took 1 damage.\n"
                         "1/390 Dummy Minion took 5 damage.\n"
                         "5/0 Dummy Minion died.\n"
                         "6/1 Dummy Minion attacks 1/390 Dummy Minion.\n"
                         "1/384 Dummy Minion took 6 damage.\n"
                         "6/0 Dummy Minion took 1 damage.\n"
                         "6/0 Dummy Minion died.\n"
                         "Combat is over.\n"
                         "Player 0 dealt 7 damage to Player 1.\n")

    def test_attack_order_multiple_rounds(self):
        game = setup_game(123, "1/30 minion, 2/30 minion, 3/30 minion | 4/30 minion, 5/30 minion, 6/30 minion")
        game.battle(1, 0)
        self.maxDiff = None
        self.assertEqual(game.test_log,
                         "Started combat between Player 0 and Player 1.\n"
                         "4/30 Dummy Minion attacks 1/30 Dummy Minion.\n"
                         "1/26 Dummy Minion took 4 damage.\n"
                         "4/29 Dummy Minion took 1 damage.\n"
                         "1/26 Dummy Minion attacks 6/30 Dummy Minion.\n"
                         "6/29 Dummy Minion took 1 damage.\n"
                         "1/20 Dummy Minion took 6 damage.\n"
                         "5/30 Dummy Minion attacks 1/20 Dummy Minion.\n"
                         "1/15 Dummy Minion took 5 damage.\n"
                         "5/29 Dummy Minion took 1 damage.\n"
                         "2/30 Dummy Minion attacks 4/29 Dummy Minion.\n"
                         "4/27 Dummy Minion took 2 damage.\n"
                         "2/26 Dummy Minion took 4 damage.\n"
                         "6/29 Dummy Minion attacks 1/15 Dummy Minion.\n"
                         "1/9 Dummy Minion took 6 damage.\n"
                         "6/28 Dummy Minion took 1 damage.\n"
                         "3/30 Dummy Minion attacks 5/29 Dummy Minion.\n"
                         "5/26 Dummy Minion took 3 damage.\n"
                         "3/25 Dummy Minion took 5 damage.\n"
                         "4/27 Dummy Minion attacks 2/26 Dummy Minion.\n"
                         "2/22 Dummy Minion took 4 damage.\n"
                         "4/25 Dummy Minion took 2 damage.\n"
                         "1/9 Dummy Minion attacks 6/28 Dummy Minion.\n"
                         "6/27 Dummy Minion took 1 damage.\n"
                         "1/3 Dummy Minion took 6 damage.\n"
                         "5/26 Dummy Minion attacks 2/22 Dummy Minion.\n"
                         "2/17 Dummy Minion took 5 damage.\n"
                         "5/24 Dummy Minion took 2 damage.\n"
                         "2/17 Dummy Minion attacks 5/24 Dummy Minion.\n"
                         "5/22 Dummy Minion took 2 damage.\n"
                         "2/12 Dummy Minion took 5 damage.\n"
                         "6/27 Dummy Minion attacks 2/12 Dummy Minion.\n"
                         "2/6 Dummy Minion took 6 damage.\n"
                         "6/25 Dummy Minion took 2 damage.\n"
                         "3/25 Dummy Minion attacks 4/25 Dummy Minion.\n"
                         "4/22 Dummy Minion took 3 damage.\n"
                         "3/21 Dummy Minion took 4 damage.\n"
                         "4/22 Dummy Minion attacks 2/6 Dummy Minion.\n"
                         "2/2 Dummy Minion took 4 damage.\n"
                         "4/20 Dummy Minion took 2 damage.\n"
                         "1/3 Dummy Minion attacks 5/22 Dummy Minion.\n"
                         "5/21 Dummy Minion took 1 damage.\n"
                         "1/-2 Dummy Minion took 5 damage.\n"
                         "1/-2 Dummy Minion died.\n"
                         "5/21 Dummy Minion attacks 3/21 Dummy Minion.\n"
                         "3/16 Dummy Minion took 5 damage.\n"
                         "5/18 Dummy Minion took 3 damage.\n"
                         "2/2 Dummy Minion attacks 4/20 Dummy Minion.\n"
                         "4/18 Dummy Minion took 2 damage.\n"
                         "2/-2 Dummy Minion took 4 damage.\n"
                         "2/-2 Dummy Minion died.\n"
                         "6/25 Dummy Minion attacks 3/16 Dummy Minion.\n"
                         "3/10 Dummy Minion took 6 damage.\n"
                         "6/22 Dummy Minion took 3 damage.\n"
                         "3/10 Dummy Minion attacks 4/18 Dummy Minion.\n"
                         "4/15 Dummy Minion took 3 damage.\n"
                         "3/6 Dummy Minion took 4 damage.\n"
                         "4/15 Dummy Minion attacks 3/6 Dummy Minion.\n"
                         "3/2 Dummy Minion took 4 damage.\n"
                         "4/12 Dummy Minion took 3 damage.\n"
                         "3/2 Dummy Minion attacks 6/22 Dummy Minion.\n"
                         "6/19 Dummy Minion took 3 damage.\n"
                         "3/-4 Dummy Minion took 6 damage.\n"
                         "3/-4 Dummy Minion died.\n"
                         "Combat is over.\n"
                         "Player 1 dealt 4 damage to Player 0.\n")

    # TODO I get 0% win, but in the vid the guy wins
    # https://www.youtube.com/watch?v=-FQjXYYdH_c&ab_channel=ItsBen321
    # setupgame 124 unstableGhoul, scallywag, scallywag, 10/9 dreadAdmiralEliza, 3/9 baronRivendare, 3/3 khadgar, 3/3 khadgar | scallywag, 7/4 golden scallywag (deathrattle,taunt), 13/14 dreadAdmiralEliza, dreadAdmiralEliza, 3/2 khadgar, 4/4 golden khadgar
    # def test_scally_ghoul_exodia(self):
    #    game = setup_game(123, "unstableGhoul, scallywag, scallywag, 10/9 dreadAdmiralEliza, 3/9 baronRivendare, "
    #                           "3/3 khadgar, 3/3 khadgar | scallywag, 7/4 golden scallywag (taunt), "
    #                           "13/14 dreadAdmiralEliza, dreadAdmiralEliza, 3/2 khadgar, 4/4 golden khadgar")
    #    game.battle(1, 0)
    #    self.maxDiff = None
    #    self.assertEqual(game.test_log,
    #                     "")

    # https://www.youtube.com/watch?v=R15ez2bvVqU&t=1s&ab_channel=dogdog
    # setupgame 1 scallywag, 12/14 golden dreadAdmiralEliza, 4/4 golden Khadgar, baronRivendare, khadgar, amalgadon (taunt,divineshield,poisonous) | amalgadon (windfury), 8/10 siegebreaker, 9/12 siegebreaker, 11/17 Voidlord, 4/6 golden nathrezimOverseer, impMama (reborn), 6/6 golden soulJuggler
    # def test_scally_exodia_vs_juggler(self):
    #     game = setup_game(1,
    #                       "scallywag, 12/14 golden dreadAdmiralEliza, 4/4 golden Khadgar, baronRivendare, khadgar, "
    #                       "amalgadon (taunt,divineshield,poisonous) | "
    #                       "amalgadon (windfury), 8/10 siegebreaker, 9/12 siegebreaker, 11/17 Voidlord, "
    #                       "4/6 golden nathrezimOverseer, impMama, 6/6 golden soulJuggler")
    #     game.battle(1, 0)
    #     self.maxDiff = None
    #     self.assertEqual(game.test_log,
    #                      "")


if __name__ == '__main__':
    unittest.main()
