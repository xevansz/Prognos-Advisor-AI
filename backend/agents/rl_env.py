import random

from typing import List, Tuple

from agents.state_encoder import encode_state, clamp


class FinancialEnv:
    """
    A gym-like financial simulation environment
    """

    def __init__(self, initial_state: dict) -> None:
        """
        initial_state must contain:
        balance
        monthly_income
        monthly_expenses
        equity_ratio
        goal_target
        goal_months_remaining
        """

        self.initial_state = initial_state
        self.max_months = random.randint(60, 120)  # 5 - 10 years
        self.month = 0

        self._load_initial_state()

    def _load_initial_state(self):
        self.balance = self.initial_state["balance"]
        self.monthly_income = self.initial_state["monthly_income"]
        self.monthly_expenses = self.initial_state["monthly_expenses"]
        self.equity_ratio = self.initial_state["equity_ratio"]
        self.goal_target = self.initial_state["goal_target"]
        self.goal_months_remaining = self.initial_state["goal_months_remaining"]

        self.savings_rate = clamp(
            (self.monthly_income - self.monthly_expenses) / self.monthly_income
            if self.monthly_income > 0
            else 0.0,
            0.0,
            1.0,
        )

    def reset(self) -> List[float]:
        """
        Reset simulation and return initial state vector
        """
        self.month = 0
        self._load_initial_state()
        return self._get_state_vector()

    def _get_state_vector(self) -> List[float]:
        runway = (
            self.balance / (self.monthly_income * (1 - self.savings_rate))
            if self.monthly_income * (1 - self.savings_rate) > 0
            else 12
        )
        stability = (
            self.monthly_income / self.monthly_expenses
            if self.monthly_expenses > 0
            else 2.0
        )
        risk_score = (
            40 * min(runway / 12, 1)
            + 30 * min(stability / 2, 1)
            + 30 * self.savings_rate
        )

        risk_metrics = {
            "runway_months": (
                self.balance / self.monthly_expenses
                if self.monthly_expenses > 0
                else 12
            ),
            "risk_score": risk_score,
        }

        goal_evaluations = [
            {
                "success_probability": min(
                    1.0,
                    self.balance / self.goal_target if self.goal_target > 0 else 1.0,
                )
            }
        ]

        allocation = {"recommended": {"equity": self.equity_ratio}}

        return encode_state(
            risk_metrics=risk_metrics,
            goal_evaluations=goal_evaluations,
            allocation=allocation,
            monthly_savings_rate=self.savings_rate,
        )

    def step(self, action: int) -> Tuple[List[float], float, bool]:
        """
        Takes an actioni and simulates one month.
        Returns (new_state, reward, done)
        """
        previous_balance = self.balance

        self._apply_action(action)

        monthly_equity_return = random.gauss(0.07 / 12, 0.15 / 12)
        monthly_debt_return = 0.04 / 12

        investment_return = self.balance * (
            self.equity_ratio * monthly_equity_return
            + (1 - self.equity_ratio) * monthly_debt_return
        )

        monthly_savings = self.monthly_income - self.monthly_expenses

        self.balance += monthly_savings + investment_return

        self.month += 1
        self.goal_months_remaining = max(0, self.goal_months_remaining - 1)

        reward = self._calculate_reward(previous_balance)

        done = self.month >= self.max_months

        return self._get_state_vector(), reward, done

    def _apply_action(self, action: int):
        """
        0 = keep
        1 = increase savings by 5%
        2 = reduce savings by 5%
        3 = shift 10% to equity
        4 = shift 10% to bonds
        """

        if action == 1:
            self.savings_rate = clamp(self.savings_rate + 0.05, 0.0, 0.9)
            self.monthly_expenses = self.monthly_income * (1 - self.savings_rate)

        elif action == 2:
            self.savings_rate = clamp(self.savings_rate - 0.05, 0.0, 0.9)
            self.monthly_expenses = self.monthly_income * (1 - self.savings_rate)

        elif action == 3:
            self.equity_ratio = clamp(self.equity_ratio + 0.10, 0.1, 0.8)

        elif action == 4:
            self.equity_ratio = clamp(self.equity_ratio - 0.10, 0.1, 0.8)

    def _calculate_reward(self, previous_balance: float) -> float:

        net_worth_change = self.balance - previous_balance

        runway = (
            self.balance / self.monthly_expenses if self.monthly_expenses > 0 else 0
        )

        # goal
        months_left = max(self.goal_months_remaining, 1)
        projected_savings = self.balance + (
            months_left * self.monthly_income * self.savings_rate
        )

        goal_on_track = projected_savings >= self.goal_target

        reward = (
            0.01 * net_worth_change
            - (2 if runway < 3 else 0)
            + (5 if goal_on_track else -3)
        )

        return reward
