from pathlib import Path

from tinygrad import Tensor
from tinygrad.device import Device

from .dqn_model import DQNAgent
from .state_encoder import encode_state

Device.DEFAULT = "CUDA"

ACTION_MAP = {
    0: {"action": "keep_strategy", "delta": 0, "allocation_shift": {}},
    1: {"action": "increase_savings", "delta": 5, "allocation_shift": {}},
    2: {"action": "reduce_savings", "delta": -5, "allocation_shift": {}},
    3: {
        "action": "shift_to_equity",
        "delta": 0,
        "allocation_shift": {"equity": 10, "debt": -10},
    },
    4: {
        "action": "shift_to_bonds",
        "delta": 0,
        "allocation_shift": {"equity": -10, "debt": 10},
    },
}


def heuristic_strategy(state):
    risk, goal_feas, equity, savings, runway = state

    if runway < 0.25:
        return 1

    if goal_feas < 0.4:
        return 1

    if equity > 0.7:
        return 4

    if equity < 0.3 and runway > 0.5:
        return 3

    return 0


class StrategyAgent:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        self.dqn = None

        if model_path and Path(model_path).exists():
            self.dqn = DQNAgent()
            self.dqn.load(model_path)
            self.dqn.epsilon = 0.0

    def get_strategy(
        self,
        risk_metrics: dict,
        goal_evaluations: list[dict],
        allocation: dict,
        savings_rate: float,
    ):
        state = encode_state(risk_metrics, goal_evaluations, allocation, savings_rate)

        if self.dqn:
            state_tensor = Tensor(state).reshape(1, 5)
            q_values = self.dqn.network(state_tensor)
            action_idx = int(q_values.numpy().argmax())
        else:
            action_idx = heuristic_strategy(state)

        return ACTION_MAP[action_idx]
