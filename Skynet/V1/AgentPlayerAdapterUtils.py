

def get_observations(moves_left, game):
    observations = []
    for player in game.players:
        observations.append(get_observation(moves_left, player))
    return observations


# encodes board state using one hot encoding (ohe) for the minions:
def get_observation(moves_left, player):
    observation = [moves_left, player.gold]
    observation.extend(_get_offer_ohe(player, 0))
    observation.extend(_get_offer_ohe(player, 1))
    observation.extend(_get_offer_ohe(player, 2))
    observation.extend(_get_board_ohe(player, 0))
    observation.extend(_get_board_ohe(player, 1))
    observation.extend(_get_hand_ohe(player, 0))
    return observation


def execute_actions(game, action_nos, moves_left):
    rewards = []
    next_observations = []

    for i, player in enumerate(game.players):
        reward = execute_action(player, action_nos[i])
        rewards.append(reward)
        next_observations.append(get_observation(moves_left - 1, player))

    if moves_left > 1:
        return rewards, next_observations, [False] * 8

    game.combat_phase()
    for i, player in enumerate(game.players):
        rewards[i] += player.damage_history[-1]
    return rewards, next_observations, [True] * 8


# executes one action for 'player' based on the 'action_no' provided by an agent. If no moves before combat are left
# before it executes combat and adjusts reward and terminal flag accordingly.
def execute_action(player, action_no):
    reward = 0
    if action_no == 0:
        # reward += 0.1
        player.log("A.I. chose to idle.")
    elif action_no == 1:
        player.play()
    elif action_no == 2:
        player.buy(0)
    elif action_no == 3:
        player.buy(1)
    elif action_no == 4:
        player.buy(2)
    elif action_no == 5:
        player.sell(0)
    elif action_no == 6:
        player.roll()
    elif action_no == 7:
        player.freeze()

    return reward


def action_no_to_string(action_qualities):
    return "A.I. Evaluation of possible actions:" \
           "\n   idle: %.3f" % action_qualities[0] + \
           "\n   play: %.3f" % action_qualities[1] + \
           "\n   buy 0: %.3f" % action_qualities[2] + \
           "\n   buy 1: %.3f" % action_qualities[3] + \
           "\n   buy 2: %.3f" % action_qualities[4] + \
           "\n   sell: %.3f" % action_qualities[5] + \
           "\n   roll: %.3f" % action_qualities[6] + \
           "\n   freeze: %.3f" % action_qualities[7]


def _get_offer_ohe(player, index):
    ohe_minion_id = [0] * (len(player.game.minionPool.allMinions) + 1)
    if len(player.tavern.offers) > index:
        ohe_minion_id[player.tavern.offers[index].id] = 1
    return ohe_minion_id


def _get_board_ohe(player, index):
    ohe_minion_id = [0] * (len(player.game.minionPool.allMinions) + 1)
    if player.get_board_size() > index:
        ohe_minion_id[player.get_minion(index).id] = 1
    return ohe_minion_id


def _get_hand_ohe(player, index):
    ohe_minion_id = [0] * (len(player.game.minionPool.allMinions) + 1)
    if len(player.hand) > index:
        ohe_minion_id[player.hand[index].id] = 1
    return ohe_minion_id
