import random
from pathlib import Path

from tinygrad import Tensor

from agents.dqn_model import DQNAgent
from agents.rl_env import FinancialEnv

"""
At 1000 episodes, if performance fluctuates.

* If learning is unstable:
* Increase episodes to 3000
* Lower learning rate
* Increase replay buffer to 50k
* Normalize rewards
"""

MODEL_SAVE_PATH = "backend/agents/models/dqn_weights.npz"


def random_initail_state():
    return {
        "balance": random.uniform(10_000, 500_000),
        "monthly_income": random.uniform(3_000, 30_000),
        "monthly_expenses": random.uniform(2_000, 25_000),
        "equity_ratio": random.uniform(0.2, 0.8),
        "goal_target": random.uniform(50_000, 2_000_000),
        "goal_months_remaining": random.randint(12, 240),
    }


def train(episodes=1000, batch_size=32):

    Path("backend/agents/models").mkdir(parents=True, exist_ok=True)

    Tensor.training = True
    agent = DQNAgent()

    for episode in range(episodes):
        env = FinancialEnv(random_initail_state())
        state = env.reset()
        total_reward = 0

        while True:
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)

            agent.replay_buffer.push(state, action, reward, next_state, done)
            agent.train_step(batch_size=32)

            state = next_state
            total_reward += reward

            if done:
                break

        agent.decay_epsilon()

        if episode % 10 == 0:
            agent.update_target()

        if episode % 100 == 0:
            print(
                f"Episode {episode:4d} | "
                f"Reward: {total_reward:8.2f} | "
                f"Epsilon: {agent.epsilon:.4f}"
            )

    agent.save(MODEL_SAVE_PATH)
    print(f"\nTraining complete. Model saved to {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    train()
