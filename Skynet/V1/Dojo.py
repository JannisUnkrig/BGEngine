import tensorflow as tf
import numpy as np

from Simulator.Game import Game
from Skynet.V1.Agent import Agent, IgnorantAgent
from Skynet.V1.AgentPlayerAdapterUtils import get_observation, get_observations, execute_actions


class Dojo:

    def __init__(self, mf=None):
        tf.compat.v1.disable_eager_execution()
        self.mf = mf
        self.len_state = len(get_observation(-1, Game().activePlayer))
        self.agents = []
        self.create_new_agents()
        self.continue_training = True

        self.epsilon_history = []
        self.error_history = []

    def create_new_agents(self):
        self.agents = [Agent(agent_no=i, gamma=0.99, epsilon=1.0, learning_rate=0.001, input_dims=self.len_state,
                             n_actions=8, mem_size=1000000, batch_size=64, epsilon_end=0.01)
                       for i in range(8)]

    def train_agents(self, moves_until_combat, n_games=None):
        episode_no = 0
        self.continue_training = True
        while self.continue_training:
            game = Game()
            episode_no += 1
            moves_errors = []
            cur_episodes_agents_rewards = [0] * 8

            for moves_left in range(moves_until_combat, 0, -1):
                agents_errors_cur_move = []
                observations = get_observations(moves_left, game)
                action_nos = []

                for i, a in enumerate(self.agents):
                    action_nos.append(a.choose_action(observations[i]))
                rewards, next_observations, terminals = execute_actions(game, action_nos, moves_left)
                for i, a in enumerate(self.agents):
                    a.store_transition(observations[i], action_nos[i], rewards[i], next_observations[i], terminals[i])
                    error_cur_agent = a.learn()
                    agents_errors_cur_move.append(error_cur_agent)
                    cur_episodes_agents_rewards[i] += rewards[i]

                error_cur_move = np.mean(agents_errors_cur_move)
                moves_errors.append(error_cur_move)

            cur_episodes_epsilon = self.agents[0].epsilon
            self.epsilon_history.append(cur_episodes_epsilon)
            cur_episodes_error = np.mean(moves_errors)
            self.error_history.append(cur_episodes_error)

            if self.mf is None or self.mf.doLog:
                print('Episode:', episode_no,
                      '  Epsilon: %.2f' % cur_episodes_epsilon,
                      '  Avg. Error: %.4f' % cur_episodes_error,
                      '  Players cumulative rewards:', str(cur_episodes_agents_rewards))

            if n_games is not None and episode_no >= n_games:
                self.log("Done training.")
                break

    # Returns agents average performance over last n_games
    def evaluate_agents(self, moves_until_combat, n_games=100):

        ignorant_agents = []
        for agent in self.agents:
            ignorant_agents.append(IgnorantAgent(agent.q_eval))

        agents_rewards_history = []

        for episode_no in range(n_games):
            game = Game()
            cur_episodes_agents_rewards = [0] * 8

            for moves_left in range(moves_until_combat, 0, -1):
                observations = get_observations(moves_left, game)
                action_nos = []

                for i, a in enumerate(ignorant_agents):
                    action_nos.append(a.choose_action(observations[i]))

                rewards, _, __ = execute_actions(game, action_nos, moves_left)

                for i, a in enumerate(ignorant_agents):
                    cur_episodes_agents_rewards[i] += rewards[i]

            agents_rewards_history.append(cur_episodes_agents_rewards)

        return np.mean(np.array(agents_rewards_history), axis=0)

    def save_agents(self):
        self.log("Starting to save agent models")
        for agent in self.agents:
            agent.save_model()
            self.log("Saved Agent" + str(agent.agent_no))

    def load_agents(self):
        self.log("Starting to load agent models")
        self.create_new_agents()
        for agent in self.agents:
            agent.load_model()
            self.log("Loaded Agent" + str(agent.agent_no))

    def log(self, text):
        if self.mf is not None:
            self.mf.log(text)
