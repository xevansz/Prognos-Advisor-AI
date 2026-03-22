import random

from agents.state_encoder import clamp, encode_state


def calculate_goal_feasibility(
    current_balance: float,
    monthly_savings: float,
    goal_target: float,
    months_remaining: int,
    expected_annual_return: float = 0.07,
) -> float:
    """
    Calculate goal success probability using deterministic future value projection.
    This is a lightweight version of the Monte Carlo approach in goal_agent.py,
    suitable for RL training.

    Returns:
        Success probability estimate in [0, 1]
    """
    if months_remaining <= 0 or goal_target <= 0:
        return 1.0 if current_balance >= goal_target else 0.0

    monthly_rate = expected_annual_return / 12.0

    if monthly_rate > 0:
        future_value_savings = current_balance * ((1 + monthly_rate) ** months_remaining)
        future_value_contributions = monthly_savings * (((1 + monthly_rate) ** months_remaining - 1) / monthly_rate)
        projected_value = future_value_savings + future_value_contributions
    else:
        projected_value = current_balance + (monthly_savings * months_remaining)

    if projected_value >= goal_target:
        ratio = projected_value / goal_target
        return min(1.0, 0.75 + (ratio - 1.0) * 0.1)
    else:
        ratio = projected_value / goal_target
        if ratio >= 0.9:
            return 0.65
        elif ratio >= 0.75:
            return 0.50
        elif ratio >= 0.5:
            return 0.30
        else:
            return 0.15


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

        # Market regime: normal, bull, bear, recession
        self.market_regime = "normal"
        self.months_in_regime = 0
        self.regime_duration = random.randint(12, 36)

        self._load_initial_state()

    def _load_initial_state(self):
        self.balance = self.initial_state["balance"]
        self.monthly_income = self.initial_state["monthly_income"]
        self.monthly_expenses = self.initial_state["monthly_expenses"]
        self.equity_ratio = self.initial_state["equity_ratio"]
        self.goal_target = self.initial_state["goal_target"]
        self.goal_months_remaining = self.initial_state["goal_months_remaining"]

        self.savings_rate = clamp(
            ((self.monthly_income - self.monthly_expenses) / self.monthly_income if self.monthly_income > 0 else 0.0),
            0.0,
            1.0,
        )

    def reset(self) -> list[float]:
        """
        Reset simulation and return initial state vector
        """
        self.month = 0
        self._load_initial_state()
        return self._get_state_vector()

    def _get_state_vector(self) -> list[float]:
        runway_months = self.balance / self.monthly_expenses if self.monthly_expenses > 0 else 12
        stability = self.monthly_income / self.monthly_expenses if self.monthly_expenses > 0 else 2.0

        def normalize(value: float, min_val: float, max_val: float) -> float:
            if max_val == min_val:
                return 0.5
            normalized = (value - min_val) / (max_val - min_val)
            return max(0.0, min(1.0, normalized))

        runway_normalized = normalize(min(runway_months, 12.0), 0.0, 12.0)
        stability_normalized = normalize(stability, 0.5, 2.0)
        risk_score = 40 * runway_normalized + 30 * stability_normalized + 30 * self.savings_rate

        risk_metrics = {
            "runway_months": runway_months,
            "risk_score": risk_score,
        }

        monthly_savings = self.monthly_income * self.savings_rate
        success_probability = calculate_goal_feasibility(
            current_balance=self.balance,
            monthly_savings=monthly_savings,
            goal_target=self.goal_target,
            months_remaining=self.goal_months_remaining,
            expected_annual_return=0.07,
        )

        goal_evaluations = [
            {
                "success_probability": success_probability,
            }
        ]

        allocation = {"recommended": {"equity": self.equity_ratio}}

        return encode_state(
            risk_metrics=risk_metrics,
            goal_evaluations=goal_evaluations,
            allocation=allocation,
            monthly_savings_rate=self.savings_rate,
        )

    def step(self, action: int) -> tuple[list[float], float, bool]:
        """
        Takes an action and simulates one month.
        Returns (new_state, reward, done)
        """
        previous_balance = self.balance

        self._apply_action(action)

        # Update market regime periodically
        self._update_market_regime()

        # Get regime-dependent returns
        monthly_equity_return, monthly_debt_return = self._get_market_returns()

        investment_return = self.balance * (
            self.equity_ratio * monthly_equity_return + (1 - self.equity_ratio) * monthly_debt_return
        )

        # Apply income/expense shocks occasionally
        self._apply_shocks()

        monthly_savings = self.monthly_income - self.monthly_expenses

        self.balance += monthly_savings + investment_return
        self.balance = max(0, self.balance)  # Prevent negative balance

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

    def _update_market_regime(self):
        """Update market regime periodically to simulate economic cycles"""
        self.months_in_regime += 1

        if self.months_in_regime >= self.regime_duration:
            # Transition to new regime
            regimes = ["normal", "bull", "bear", "recession"]
            # Weighted transition probabilities
            if self.market_regime == "normal":
                self.market_regime = random.choices(regimes, weights=[0.5, 0.3, 0.15, 0.05])[0]
            elif self.market_regime == "bull":
                self.market_regime = random.choices(regimes, weights=[0.5, 0.2, 0.2, 0.1])[0]
            elif self.market_regime == "bear":
                self.market_regime = random.choices(regimes, weights=[0.5, 0.1, 0.3, 0.1])[0]
            else:  # recession
                self.market_regime = random.choices(regimes, weights=[0.6, 0.1, 0.2, 0.1])[0]

            self.months_in_regime = 0
            self.regime_duration = random.randint(12, 36)

    def _get_market_returns(self) -> tuple[float, float]:
        """Get market returns based on current regime"""
        regime_params = {
            "normal": {"equity_mean": 0.07 / 12, "equity_std": 0.15 / 12, "debt": 0.04 / 12},
            "bull": {"equity_mean": 0.12 / 12, "equity_std": 0.12 / 12, "debt": 0.035 / 12},
            "bear": {"equity_mean": -0.05 / 12, "equity_std": 0.20 / 12, "debt": 0.045 / 12},
            "recession": {"equity_mean": -0.15 / 12, "equity_std": 0.25 / 12, "debt": 0.03 / 12},
        }

        params = regime_params[self.market_regime]
        monthly_equity_return = random.gauss(params["equity_mean"], params["equity_std"])
        monthly_debt_return = params["debt"]

        return monthly_equity_return, monthly_debt_return

    def _apply_shocks(self):
        """Apply occasional income or expense shocks"""
        # 5% chance of income shock each month
        if random.random() < 0.05:
            shock_type = random.choice(["income_boost", "income_loss", "expense_spike"])

            if shock_type == "income_boost":
                # Bonus or raise: 10-30% increase for this month
                self.monthly_income *= random.uniform(1.1, 1.3)
            elif shock_type == "income_loss":
                # Temporary income reduction: 20-40% decrease
                self.monthly_income *= random.uniform(0.6, 0.8)
            elif shock_type == "expense_spike":
                # Unexpected expense: 20-50% increase
                self.monthly_expenses *= random.uniform(1.2, 1.5)

            # Update savings rate based on new income/expenses
            if self.monthly_income > 0:
                self.savings_rate = clamp((self.monthly_income - self.monthly_expenses) / self.monthly_income, 0.0, 0.9)

    def _calculate_reward(self, previous_balance: float) -> float:
        net_worth_change = self.balance - previous_balance

        runway = self.balance / self.monthly_expenses if self.monthly_expenses > 0 else 0

        # Use paper-faithful goal feasibility
        monthly_savings = self.monthly_income * self.savings_rate
        success_probability = calculate_goal_feasibility(
            current_balance=self.balance,
            monthly_savings=monthly_savings,
            goal_target=self.goal_target,
            months_remaining=self.goal_months_remaining,
            expected_annual_return=0.07,
        )

        goal_on_track = success_probability >= 0.75

        reward = 0.01 * net_worth_change - (2 if runway < 3 else 0) + (5 if goal_on_track else -3)

        return reward
