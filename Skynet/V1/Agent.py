from Skynet.V1.ReplayBuffer import ReplayBuffer

import numpy as np
from tensorflow import keras
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
import tensorflow.python.util.deprecation as depr
depr._PRINT_DEPRECATION_WARNINGS = False


class Agent:

    def __init__(self, learning_rate, gamma, n_actions, epsilon, batch_size, input_dims, agent_no, epsilon_dec=0.005,
                 epsilon_end=0.01, mem_size=1000000, file_path_and_name='AgentModels/dqn_model_agent_'):
        self.agent_no = agent_no
        self.action_space = [i for i in range(n_actions)]
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_end
        self.epsilon_dec = epsilon_dec
        self.batch_size = batch_size
        self.model_file = file_path_and_name + str(agent_no)
        self.memory = ReplayBuffer(mem_size, input_dims)
        self.q_eval = build_dqn(learning_rate, n_actions, 256, 256)

    def store_transition(self, state, action, reward, new_state, terminal):
        self.memory.store_transition(state, action, reward, new_state, terminal)

    def choose_action(self, observation):
        if np.random.random() < self.epsilon:
            action = np.random.choice(self.action_space)
        else:
            state = np.array([observation])
            action_qualities = self.q_eval.predict(state)
            action = np.argmax(action_qualities)
        return action

    # returns mean squared error (mse) of this learning session
    def learn(self):
        if self.memory.mem_counter < self.batch_size:
            return -1

        states, actions, rewards, new_states, terminals = self.memory.sample_buffer(self.batch_size)

        q_eval = self.q_eval.predict(states)
        q_next = self.q_eval.predict(new_states)

        q_target = np.copy(q_eval)
        batch_index = np.arange(self.batch_size, dtype=np.int32)

        q_target[batch_index, actions] = rewards + self.gamma * np.max(q_next, axis=1) * terminals

        self.q_eval.train_on_batch(states, q_target)

        self.epsilon = self.epsilon - self.epsilon_dec if self.epsilon > self.epsilon_min else self.epsilon_min

        error_all_actions = np.absolute(np.subtract(q_eval, q_target))
        avg_error = np.sum(error_all_actions) / self.batch_size
        return avg_error

    def save_model(self):
        self.q_eval.save(self.model_file)

    def load_model(self):
        self.q_eval = load_model(self.model_file)


class IgnorantAgent:

    def __init__(self, file_path_and_name):
        self.q_eval = load_model(file_path_and_name)

    def choose_action(self, observation):
        state = np.array([observation])
        action_qualities = self.q_eval.predict(state)
        action = np.argmax(action_qualities)
        return action

    def evaluate_actions(self, observation):
        state = np.array([observation])
        action_qualities = self.q_eval.predict(state)
        return action_qualities.tolist()[0]


def build_dqn(learning_rate, n_actions, fc1_dims, fc2_dims):
    model = keras.Sequential([
        keras.layers.Dense(fc1_dims, activation='relu'),
        keras.layers.Dense(fc2_dims, activation='relu'),
        keras.layers.Dense(n_actions, activation=None)])
    model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mean_squared_error')
    return model
