from tinygrad import Tensor, nn
from tinygrad.nn.state import get_state_dict, get_parameters, load_state_dict
import random
from collections import deque
import numpy as np


class QNetwork:
    def __init__(self):
        self.l1 = nn.Linear(5, 64)
        self.l2 = nn.Linear(64, 32)
        self.l3 = nn.Linear(32, 5)

    def __call__(self, x: Tensor) -> Tensor:
        x = self.l1(x).relu()
        x = self.l2(x).relu()
        return self.l3(x)

    def parameters(self):
        return get_parameters(self)


class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size=32):
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)


class DQNAgent:
    def __init__(
        self,
        gamma=0.99,
        lr=0.001,
        epsilon_start=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.995,
    ):
        self.network = QNetwork()
        self.target_network = QNetwork()
        self.update_target()

        self.gamma = gamma
        self.lr = lr

        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        self.replay_buffer = ReplayBuffer()

        self.optimizer = nn.optim.Adam(get_parameters(self.network), lr=self.lr)

    # Action selection
    def select_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 4)

        state_tensor = Tensor(state).reshape(1, 5)
        q_values = self.network(state_tensor)
        return int(q_values.numpy().argmax())

    def train_step(self, batch_size=32):
        if len(self.replay_buffer) < batch_size:
            return

        batch = self.replay_buffer.sample(batch_size)

        states = np.array([b[0] for b in batch])
        actions = np.array([b[1] for b in batch])
        rewards = np.array([b[2] for b in batch])
        next_states = np.array([b[3] for b in batch])
        dones = np.array([b[4] for b in batch])

        states = Tensor(states)
        next_states = Tensor(next_states)
        rewards = Tensor(rewards)
        dones = Tensor(dones)

        # Current Q valeus
        q_values = self.network(states)

        # next q values
        next_q_values = self.target_network(next_states).max(axis=1)

        target_q = rewards + (1 - dones) * self.gamma * next_q_values

        # gather Q values for taken actions (tinygrad doesn't support advanced indexing)
        action_mask = Tensor.eye(5)[Tensor(actions)]
        q_selected = (q_values * action_mask).sum(axis=1)

        loss = (q_selected - target_q).square().mean()

        # backprop
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    # Target Network update
    def update_target(self):
        state_dict = get_state_dict(self.network)
        load_state_dict(self.target_network, state_dict)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    # save and load
    def save(self, path="dqn_model.npz"):
        state_dict = get_state_dict(self.network)
        np_dict = {k: v.numpy() for k, v in state_dict.items()}
        np.savez(path, **np_dict)

    def load(self, path="dqn_model.npz"):
        data = np.load(path)
        tensor_dict = {k: Tensor(v) for k, v in data.items()}
        load_state_dict(self.network, tensor_dict)
        self.update_target()
