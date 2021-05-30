
import tensorflow as tf
import numpy as np

from Simulator.Game import Game
from Skynet.V1.Agent import Agent
from Skynet.V1.AgentPlayerAdapterUtils import get_observation, get_observations, execute_actions


def train_new_agents():
    tf.compat.v1.disable_eager_execution()

    n_games = 100
    moves_until_combat = 10
    len_state = len(get_observation(0, Game().activePlayer))
    agents = [Agent(agent_no=i, gamma=0.99, epsilon=1.0, learning_rate=0.001, input_dims=len_state, n_actions=8,
                    mem_size=1000000, batch_size=64, epsilon_end=0.01,
                    file_path_and_name='AgentModels/dqn_model_agent_') for i in range(8)]

    epsilon_history = []
    error_history = []
    agents_rewards_history = []

    for episode_no in range(n_games):
        game = Game()
        moves_errors = []
        cur_episodes_agents_rewards = [0] * 8

        for moves_left in range(moves_until_combat, 0, -1):
            agents_errors_cur_move = []
            observations = get_observations(moves_left, game)
            action_nos = []

            for i, a in enumerate(agents):
                action_nos.append(a.choose_action(observations[i]))
            rewards, next_observations, terminals = execute_actions(game, action_nos, moves_left)
            for i, a in enumerate(agents):
                a.store_transition(observations[i], action_nos[i], rewards[i], next_observations[i], terminals[i])
                error_cur_agent = a.learn()
                agents_errors_cur_move.append(error_cur_agent)
                cur_episodes_agents_rewards[i] += rewards[i]

            error_cur_move = np.mean(agents_errors_cur_move)
            moves_errors.append(error_cur_move)

        cur_episodes_epsilon = agents[0].epsilon
        epsilon_history.append(cur_episodes_epsilon)
        cur_episodes_error = np.mean(moves_errors)
        error_history.append(cur_episodes_error)

        if n_games - episode_no < 100:
            agents_rewards_history.append(cur_episodes_agents_rewards)

        print('Episode:', episode_no + 1,
              '  Epsilon: %.2f' % cur_episodes_epsilon,
              '  Avg. Error: %.4f' % cur_episodes_error,
              '  Players cumulative rewards:', str(cur_episodes_agents_rewards))

    agent_performances = np.mean(np.array(agents_rewards_history), axis=0)
    print('Agents average performances over last 100 episodes:', str(agent_performances))

    print('Starting to save agents models')
    for agent in agents:
        agent.save_model()
        print('Saved Agent', agent.agent_no)


if __name__ == '__main__':
    train_new_agents()
