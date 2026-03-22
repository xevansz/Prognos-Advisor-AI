import json
import random
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
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

MODEL_SAVE_PATH = "agents/models/dqn_weights.npz"


def random_initial_state():
    return {
        "balance": random.uniform(10_000, 500_000),
        "monthly_income": random.uniform(3_000, 30_000),
        "monthly_expenses": random.uniform(2_000, 25_000),
        "equity_ratio": random.uniform(0.2, 0.8),
        "goal_target": random.uniform(50_000, 2_000_000),
        "goal_months_remaining": random.randint(12, 240),
    }


def moving_average(data, window_size):
    """Calculate moving average for smoothing"""
    if len(data) < window_size:
        return data
    return np.convolve(data, np.ones(window_size) / window_size, mode="valid")


def plot_training_metrics(metrics, save_dir):
    """Generate paper-ready plots from training metrics"""
    episodes = list(range(len(metrics["episode_rewards"])))
    rewards = metrics["episode_rewards"]

    # Create figure with high DPI for paper quality
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    fig.suptitle("DQN Training Metrics", fontsize=16, fontweight="bold")

    # Plot 1: Reward trajectory with smoothing
    ax1 = axes[0, 0]
    ax1.plot(episodes, rewards, alpha=0.3, color="blue", label="Raw Reward")
    if len(rewards) >= 50:
        smoothed = moving_average(rewards, 50)
        smooth_episodes = episodes[: len(smoothed)]
        ax1.plot(smooth_episodes, smoothed, color="darkblue", linewidth=2, label="50-Episode MA")
    ax1.set_xlabel("Episode", fontsize=12)
    ax1.set_ylabel("Cumulative Reward", fontsize=12)
    ax1.set_title("Training Reward Trajectory", fontsize=13, fontweight="bold")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Episode length
    ax2 = axes[0, 1]
    ax2.plot(episodes, metrics["episode_lengths"], color="green", alpha=0.6)
    if len(metrics["episode_lengths"]) >= 50:
        smoothed_len = moving_average(metrics["episode_lengths"], 50)
        ax2.plot(episodes[: len(smoothed_len)], smoothed_len, color="darkgreen", linewidth=2)
    ax2.set_xlabel("Episode", fontsize=12)
    ax2.set_ylabel("Episode Length (months)", fontsize=12)
    ax2.set_title("Episode Duration", fontsize=13, fontweight="bold")
    ax2.grid(True, alpha=0.3)

    # Plot 3: Terminal balance
    ax3 = axes[1, 0]
    ax3.plot(episodes, metrics["terminal_balances"], color="purple", alpha=0.6)
    if len(metrics["terminal_balances"]) >= 50:
        smoothed_bal = moving_average(metrics["terminal_balances"], 50)
        ax3.plot(episodes[: len(smoothed_bal)], smoothed_bal, color="darkviolet", linewidth=2)
    ax3.set_xlabel("Episode", fontsize=12)
    ax3.set_ylabel("Terminal Balance ($)", fontsize=12)
    ax3.set_title("Final Net Worth", fontsize=13, fontweight="bold")
    ax3.grid(True, alpha=0.3)

    # Plot 4: Goal achievement rate
    ax4 = axes[1, 1]
    goal_rate = metrics["goal_on_track_rate"]
    ax4.plot(episodes, goal_rate, color="orange", alpha=0.6)
    if len(goal_rate) >= 50:
        smoothed_goal = moving_average(goal_rate, 50)
        ax4.plot(episodes[: len(smoothed_goal)], smoothed_goal, color="darkorange", linewidth=2)
    ax4.set_xlabel("Episode", fontsize=12)
    ax4.set_ylabel("Goal Achievement Rate", fontsize=12)
    ax4.set_title("Goal Success Probability", fontsize=13, fontweight="bold")
    ax4.axhline(y=0.75, color="red", linestyle="--", alpha=0.5, label="On-Track Threshold")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save as both PNG and PDF for paper flexibility
    png_path = save_dir / "training_metrics.png"
    pdf_path = save_dir / "training_metrics.pdf"
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.savefig(pdf_path, bbox_inches="tight")
    plt.close()

    print(f"Plots saved to {png_path} and {pdf_path}")


def save_metrics_summary(metrics, save_dir, config):
    """Save metrics summary as JSON and CSV for analysis"""
    # Calculate summary statistics
    rewards = metrics["episode_rewards"]
    summary = {
        "config": config,
        "timestamp": datetime.now().isoformat(),
        "total_episodes": len(rewards),
        "final_epsilon": metrics["final_epsilon"],
        "reward_stats": {
            "mean": float(np.mean(rewards)),
            "std": float(np.std(rewards)),
            "min": float(np.min(rewards)),
            "max": float(np.max(rewards)),
            "final_100_mean": float(np.mean(rewards[-100:])) if len(rewards) >= 100 else float(np.mean(rewards)),
        },
        "terminal_balance_stats": {
            "mean": float(np.mean(metrics["terminal_balances"])),
            "std": float(np.std(metrics["terminal_balances"])),
            "final_100_mean": float(np.mean(metrics["terminal_balances"][-100:]))
            if len(metrics["terminal_balances"]) >= 100
            else float(np.mean(metrics["terminal_balances"])),
        },
        "goal_achievement": {
            "mean_success_rate": float(np.mean(metrics["goal_on_track_rate"])),
            "final_100_mean": float(np.mean(metrics["goal_on_track_rate"][-100:]))
            if len(metrics["goal_on_track_rate"]) >= 100
            else float(np.mean(metrics["goal_on_track_rate"])),
        },
        "runway_stats": {
            "mean_min_runway": float(np.mean(metrics["min_runway_per_episode"])),
            "low_runway_episodes": int(np.sum(np.array(metrics["min_runway_per_episode"]) < 3)),
        },
    }

    # Save JSON summary
    json_path = save_dir / "training_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Save detailed CSV
    csv_path = save_dir / "training_metrics.csv"
    with open(csv_path, "w") as f:
        f.write("episode,reward,length,terminal_balance,goal_on_track,min_runway,epsilon\n")
        for i in range(len(rewards)):
            f.write(
                f"{i},{rewards[i]},{metrics['episode_lengths'][i]},"
                f"{metrics['terminal_balances'][i]},{metrics['goal_on_track_rate'][i]},"
                f"{metrics['min_runway_per_episode'][i]},{metrics['epsilon_history'][i]}\n"
            )

    print(f"Metrics saved to {json_path} and {csv_path}")
    print("\nTraining Summary:")
    print(f"  Mean Reward: {summary['reward_stats']['mean']:.2f} ± {summary['reward_stats']['std']:.2f}")
    print(f"  Final 100 Episodes Mean Reward: {summary['reward_stats']['final_100_mean']:.2f}")
    print(f"  Mean Terminal Balance: ${summary['terminal_balance_stats']['mean']:.2f}")
    print(f"  Goal Achievement Rate: {summary['goal_achievement']['mean_success_rate']:.2%}")
    print(f"  Low Runway Episodes: {summary['runway_stats']['low_runway_episodes']}")


def train(episodes=1000, batch_size=32, seed=None):
    """Train DQN agent with comprehensive metrics tracking"""
    # Set random seed for reproducibility
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # Create output directories
    models_dir = Path("agents/models")
    models_dir.mkdir(parents=True, exist_ok=True)

    Tensor.training = True
    agent = DQNAgent()

    # Metrics tracking
    metrics = {
        "episode_rewards": [],
        "episode_lengths": [],
        "terminal_balances": [],
        "goal_on_track_rate": [],
        "min_runway_per_episode": [],
        "epsilon_history": [],
        "final_epsilon": 0.0,
    }

    config = {
        "episodes": episodes,
        "batch_size": batch_size,
        "gamma": agent.gamma,
        "learning_rate": agent.lr,
        "epsilon_start": 1.0,
        "epsilon_min": agent.epsilon_min,
        "epsilon_decay": agent.epsilon_decay,
        "replay_buffer_size": 10000,
        "seed": seed,
    }

    print(f"Starting training for {episodes} episodes...")
    print(f"Configuration: {config}")

    for episode in range(episodes):
        env = FinancialEnv(random_initial_state())
        state = env.reset()
        total_reward = 0
        episode_length = 0
        min_runway = float("inf")

        while True:
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)

            agent.replay_buffer.push(state, action, reward, next_state, done)
            agent.train_step(batch_size=batch_size)

            state = next_state
            total_reward += reward
            episode_length += 1

            # Track minimum runway during episode
            current_runway = env.balance / env.monthly_expenses if env.monthly_expenses > 0 else 0
            min_runway = min(min_runway, current_runway)

            if done:
                break

        # Record metrics
        metrics["episode_rewards"].append(total_reward)
        metrics["episode_lengths"].append(episode_length)
        metrics["terminal_balances"].append(env.balance)

        # Calculate goal success at episode end
        monthly_savings = env.monthly_income * env.savings_rate
        from agents.rl_env import calculate_goal_feasibility

        final_goal_prob = calculate_goal_feasibility(
            current_balance=env.balance,
            monthly_savings=monthly_savings,
            goal_target=env.goal_target,
            months_remaining=env.goal_months_remaining,
            expected_annual_return=0.07,
        )
        metrics["goal_on_track_rate"].append(final_goal_prob)
        metrics["min_runway_per_episode"].append(min_runway if min_runway != float("inf") else 0)
        metrics["epsilon_history"].append(agent.epsilon)

        agent.decay_epsilon()

        if episode % 10 == 0:
            agent.update_target()

        if episode % 100 == 0:
            recent_reward = np.mean(metrics["episode_rewards"][-100:]) if episode >= 100 else total_reward
            print(
                f"Episode {episode:4d} | Reward: {total_reward:8.2f} | "
                f"Avg(100): {recent_reward:8.2f} | Epsilon: {agent.epsilon:.4f}"
            )

    metrics["final_epsilon"] = agent.epsilon

    # Save model
    agent.save(MODEL_SAVE_PATH)
    print(f"\nModel saved to {MODEL_SAVE_PATH}")

    # Generate plots and save metrics
    plot_training_metrics(metrics, models_dir)
    save_metrics_summary(metrics, models_dir, config)

    print("\nTraining complete!")
    return metrics


if __name__ == "__main__":
    # Use a fixed seed for reproducibility in paper-reported runs
    train(seed=42)
