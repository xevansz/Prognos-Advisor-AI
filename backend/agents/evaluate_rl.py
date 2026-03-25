"""
Evaluation pipeline for DQN agent with baseline comparisons.
Supports multi-seed evaluation and statistical reporting for paper.
"""

import json
import random
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from agents.dqn_model import DQNAgent
from agents.rl_env import FinancialEnv
from agents.strategy_agent import heuristic_strategy
from agents.train_rl import random_initial_state

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


def create_evaluation_set(num_scenarios=100, seed=42):
    """Create a fixed set of evaluation scenarios for reproducible testing"""
    random.seed(seed)
    np.random.seed(seed)

    scenarios = []
    for _ in range(num_scenarios):
        scenarios.append(random_initial_state())

    return scenarios


def evaluate_agent(agent, scenarios, agent_name="DQN"):
    """Evaluate an agent on a fixed set of scenarios"""
    results = {
        "total_rewards": [],
        "terminal_balances": [],
        "goal_success_rates": [],
        "min_runways": [],
        "episode_lengths": [],
        "low_runway_count": 0,
    }

    for scenario in scenarios:
        env = FinancialEnv(scenario)
        state = env.reset()
        total_reward = 0
        min_runway = float("inf")

        while True:
            if agent_name == "DQN":
                action = agent.select_action(state)
            elif agent_name == "Heuristic":
                action = heuristic_strategy(state)
            elif agent_name == "Random":
                action = random.randint(0, 4)
            else:  # Keep strategy
                action = 0

            next_state, reward, done = env.step(action)

            state = next_state
            total_reward += reward

            current_runway = env.balance / env.monthly_expenses if env.monthly_expenses > 0 else 0
            min_runway = min(min_runway, current_runway)

            if done:
                break

        # Record results
        results["total_rewards"].append(total_reward)
        results["terminal_balances"].append(env.balance)

        # Calculate final goal success
        monthly_savings = env.monthly_income * env.savings_rate
        from agents.rl_env import calculate_goal_feasibility

        final_goal_prob = calculate_goal_feasibility(
            current_balance=env.balance,
            monthly_savings=monthly_savings,
            goal_target=env.goal_target,
            months_remaining=env.goal_months_remaining,
            expected_annual_return=0.07,
        )
        results["goal_success_rates"].append(final_goal_prob)
        results["min_runways"].append(min_runway if min_runway != float("inf") else 0)
        results["episode_lengths"].append(env.month)

        if min_runway < 3:
            results["low_runway_count"] += 1

    return results


def compute_statistics(results):
    """Compute summary statistics from evaluation results"""
    return {
        "reward": {
            "mean": float(np.mean(results["total_rewards"])),
            "std": float(np.std(results["total_rewards"])),
            "median": float(np.median(results["total_rewards"])),
        },
        "terminal_balance": {
            "mean": float(np.mean(results["terminal_balances"])),
            "std": float(np.std(results["terminal_balances"])),
            "median": float(np.median(results["terminal_balances"])),
        },
        "goal_success": {
            "mean": float(np.mean(results["goal_success_rates"])),
            "std": float(np.std(results["goal_success_rates"])),
            "on_track_rate": float(np.mean([1 if x >= 0.75 else 0 for x in results["goal_success_rates"]])),
        },
        "runway": {
            "mean_min": float(np.mean(results["min_runways"])),
            "low_runway_episodes": results["low_runway_count"],
            "low_runway_rate": results["low_runway_count"] / len(results["total_rewards"]),
        },
    }


def plot_baseline_comparison(all_results, save_dir):
    """Generate comparison plots between DQN and baselines"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    fig.suptitle("DQN vs Baseline Comparison", fontsize=16, fontweight="bold")

    agents = list(all_results.keys())
    colors = {"DQN": "blue", "Heuristic": "green", "Keep": "orange", "Random": "red"}

    # Plot 1: Mean rewards comparison
    ax1 = axes[0, 0]
    means = [all_results[agent]["stats"]["reward"]["mean"] for agent in agents]
    stds = [all_results[agent]["stats"]["reward"]["std"] for agent in agents]
    x_pos = np.arange(len(agents))
    ax1.bar(x_pos, means, yerr=stds, color=[colors.get(a, "gray") for a in agents], alpha=0.7, capsize=5)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(agents)
    ax1.set_ylabel("Mean Cumulative Reward", fontsize=12)
    ax1.set_title("Reward Comparison", fontsize=13, fontweight="bold")
    ax1.grid(True, alpha=0.3, axis="y")

    # Plot 2: Terminal balance comparison
    ax2 = axes[0, 1]
    means = [all_results[agent]["stats"]["terminal_balance"]["mean"] for agent in agents]
    stds = [all_results[agent]["stats"]["terminal_balance"]["std"] for agent in agents]
    ax2.bar(x_pos, means, yerr=stds, color=[colors.get(a, "gray") for a in agents], alpha=0.7, capsize=5)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(agents)
    ax2.set_ylabel("Mean Terminal Balance ($)", fontsize=12)
    ax2.set_title("Final Net Worth Comparison", fontsize=13, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="y")

    # Plot 3: Goal achievement rate
    ax3 = axes[1, 0]
    rates = [all_results[agent]["stats"]["goal_success"]["on_track_rate"] for agent in agents]
    ax3.bar(x_pos, rates, color=[colors.get(a, "gray") for a in agents], alpha=0.7)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(agents)
    ax3.set_ylabel("Goal On-Track Rate", fontsize=12)
    ax3.set_title("Goal Achievement Comparison", fontsize=13, fontweight="bold")
    ax3.axhline(y=0.75, color="red", linestyle="--", alpha=0.5, label="Target Threshold")
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis="y")
    ax3.set_ylim([0, 1])

    # Plot 4: Low runway rate
    ax4 = axes[1, 1]
    low_runway_rates = [all_results[agent]["stats"]["runway"]["low_runway_rate"] for agent in agents]
    ax4.bar(x_pos, low_runway_rates, color=[colors.get(a, "gray") for a in agents], alpha=0.7)
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(agents)
    ax4.set_ylabel("Low Runway Episode Rate", fontsize=12)
    ax4.set_title("Financial Safety Comparison (Lower is Better)", fontsize=13, fontweight="bold")
    ax4.grid(True, alpha=0.3, axis="y")
    ax4.set_ylim([0, 1])

    plt.tight_layout()

    # Save plots
    png_path = save_dir / "baseline_comparison.png"
    pdf_path = save_dir / "baseline_comparison.pdf"
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.savefig(pdf_path, bbox_inches="tight")
    plt.close()

    print(f"Comparison plots saved to {png_path} and {pdf_path}")


def run_evaluation(model_path, num_scenarios=100, eval_seed=42):
    """Run comprehensive evaluation with baselines"""
    print(f"Running evaluation on {num_scenarios} scenarios...")

    # Create fixed evaluation set
    scenarios = create_evaluation_set(num_scenarios, seed=eval_seed)

    # Load DQN agent
    dqn_agent = DQNAgent()
    if Path(model_path).exists():
        dqn_agent.load(model_path)
        dqn_agent.epsilon = 0.0  # Disable exploration for evaluation
        print(f"Loaded DQN model from {model_path}")
    else:
        print(f"Warning: Model not found at {model_path}, using untrained agent")

    # Evaluate all agents
    all_results = {}

    print("\nEvaluating DQN agent...")
    dqn_results = evaluate_agent(dqn_agent, scenarios, "DQN")
    all_results["DQN"] = {"results": dqn_results, "stats": compute_statistics(dqn_results)}

    print("Evaluating Heuristic baseline...")
    heuristic_results = evaluate_agent(None, scenarios, "Heuristic")
    all_results["Heuristic"] = {"results": heuristic_results, "stats": compute_statistics(heuristic_results)}

    print("Evaluating Keep-Strategy baseline...")
    keep_results = evaluate_agent(None, scenarios, "Keep")
    all_results["Keep"] = {"results": keep_results, "stats": compute_statistics(keep_results)}

    print("Evaluating Random baseline...")
    random_results = evaluate_agent(None, scenarios, "Random")
    all_results["Random"] = {"results": random_results, "stats": compute_statistics(random_results)}

    # Save results
    models_dir = Path("agents/evaluate")
    models_dir.mkdir(parents=True, exist_ok=True)

    # Save detailed JSON
    eval_summary = {
        "num_scenarios": num_scenarios,
        "eval_seed": eval_seed,
        "agents": {agent: data["stats"] for agent, data in all_results.items()},
    }

    json_path = models_dir / f"evaluation_results_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(eval_summary, f, indent=2)

    print(f"\nEvaluation results saved to {json_path}")

    # Generate comparison plots
    plot_baseline_comparison(all_results, models_dir)

    # Print summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)

    for agent_name, data in all_results.items():
        stats = data["stats"]
        print(f"\n{agent_name}:")
        print(f"  Reward: {stats['reward']['mean']:.2f} ± {stats['reward']['std']:.2f}")
        print(f"  Terminal Balance: ${stats['terminal_balance']['mean']:.2f} ± ${stats['terminal_balance']['std']:.2f}")
        print(f"  Goal On-Track Rate: {stats['goal_success']['on_track_rate']:.2%}")
        print(f"  Low Runway Rate: {stats['runway']['low_runway_rate']:.2%}")

    # Calculate improvements over heuristic
    print("\n" + "=" * 80)
    print("DQN vs Heuristic Baseline:")
    print("=" * 80)

    dqn_stats = all_results["DQN"]["stats"]
    heur_stats = all_results["Heuristic"]["stats"]

    reward_improvement = (
        (dqn_stats["reward"]["mean"] - heur_stats["reward"]["mean"]) / abs(heur_stats["reward"]["mean"]) * 100
    )
    balance_improvement = (
        (dqn_stats["terminal_balance"]["mean"] - heur_stats["terminal_balance"]["mean"])
        / heur_stats["terminal_balance"]["mean"]
        * 100
    )
    goal_improvement = (dqn_stats["goal_success"]["on_track_rate"] - heur_stats["goal_success"]["on_track_rate"]) * 100

    print(f"Reward improvement: {reward_improvement:+.2f}%")
    print(f"Terminal balance improvement: {balance_improvement:+.2f}%")
    print(f"Goal achievement improvement: {goal_improvement:+.2f} percentage points")

    return all_results


if __name__ == "__main__":
    model_path = "agents/models/dqn_weights.npz"
    run_evaluation(model_path, num_scenarios=100)
