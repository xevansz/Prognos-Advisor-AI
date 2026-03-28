A Hybrid Multi-Agent Framework with Reinforcement Learning for Personalized Financial Planning and Asset Allocation

Abstract—Personal financial planning is a sequential decision problem shaped by income variability, expenditure patterns, liquidity constraints, market uncertainty, and long-horizon goals. Conventional personal finance tools are often rule-based and only weakly adaptive. This paper presents a hybrid multi-agent framework for personalized financial planning and asset allocation that combines structured financial analysis, a reinforcement-learning strategy layer, and natural-language explanation. The implemented system decomposes the task into specialized components for risk assessment, goal-feasibility evaluation, heuristic asset allocation, and strategy selection, then converts the resulting structured outputs into a user-facing report. A Deep Q-Network (DQN) is trained in a synthetic financial simulation environment in which each episode spans 60-120 monthly steps. The state representation is five-dimensional and encodes normalized risk score, goal feasibility, equity allocation, savings rate, and financial runway. In a single-seed experiment, the final 100-episode mean reward improved by 13.1% over the overall training mean, and evaluation on 100 fixed scenarios showed that the learned policy outperformed a heuristic baseline by 70.3% in cumulative reward, 49.1% in terminal balance, and 30 percentage points in goal on-track rate while maintaining comparable low-runway safety. These findings indicate that a compact RL policy can complement rule-based financial analysis in a controlled synthetic setting. Because the study relies on simulated data and single-seed evaluation, the results should be interpreted as proof-of-concept evidence rather than validated real-world advisory performance.

Index Terms—Multi-Agent Systems, Reinforcement Learning, Personal Financial Planning, Asset Allocation, Explainable AI

I. Introduction
Financial planning is central to long-term household stability and to goals such as retirement, education funding, and emergency preparedness. Although digital platforms now allow users to track balances, transactions, and investments with increasing granularity, many personal finance applications remain descriptive rather than prescriptive. They summarize spending and balances, but they do not adapt strategy as financial conditions change.

Traditional advisory and planning systems commonly rely on fixed heuristics, static risk questionnaires, or deterministic optimization rules. Such methods are transparent, but they are limited in environments where user cash flow, market conditions, and goal feasibility evolve over time. Reinforcement learning offers a natural alternative because it models planning as sequential decision making under uncertainty [2], [5], [11], [12]. In finance, RL has been applied to portfolio allocation, asset trading, and risk-aware policy adaptation, especially when decisions must balance short-term shocks against long-term outcomes [1], [2], [5], [6], [11], [12]. Interpretable variants further attempt to expose the logic of learned policies [7], [8].

However, most prior work focuses on portfolio management or trading rather than holistic personal financial planning. Personal financial planning requires simultaneous reasoning about liquidity, runway, savings behavior, goal feasibility, and broad asset-class allocation. It also requires interfaces that users can understand and trust. Recent work in robo-advising and explainable AI suggests that user adoption depends not only on performance but also on transparent explanation and preference alignment [3], [4], [9], [10].

This paper addresses that gap by presenting a hybrid multi-agent framework for personalized financial planning and asset allocation. The framework integrates a rule-based Risk Agent, a simulation-based Goal Feasibility Agent, a heuristic Investment Allocation Agent, and a Strategy Agent that can use either a learned DQN policy or a heuristic fallback. These components generate a compact financial state representation over long-horizon simulated trajectories. A language-generation layer then converts structured outputs into an interpretable report for end users. The contribution is therefore not a fully learned multi-agent control system; rather, it is an integrated personal-finance pipeline in which reinforcement learning is applied at the strategy-selection layer.

II. Literature Review
A. Introduction to Problem Domain
The relevant literature spans three connected areas: robo-advisory systems that model investor preferences, reinforcement-learning methods for portfolio management, and explainability studies concerned with trust and adoption. Portfolio-oriented RL papers show that sequential decision methods can adapt allocations to changing market states [1], [2], [5], [6], [11], [12], whereas robo-advisory studies emphasize suitability, preference elicitation, and user acceptance [3], [4], [9], [10], [13]. A complementary explainability thread argues that learned policies must be interpretable to both practitioners and end users [4], [7]–[10]. Personal financial planning sits at the intersection of these streams because it requires sequential adaptation, yet the most important state variables extend beyond market returns to liquidity, savings behavior, and goal progress.

B. Traditional Approaches
Traditional digital advice typically maps questionnaires or stated risk preferences to model portfolios using auditable rules. This paradigm remains attractive because it is easy to explain and consistent with suitability requirements. In the cited literature, [3] and [9] are closest to this tradition: [3] studies how investor preferences can be inferred from observed choices, while [9] argues that robo-advisory systems should emphasize explanation and human oversight rather than opaque automation. The strength of this line is behavioral alignment and transparency. Its limitation is scope. These approaches do not directly model household cash-flow shocks, emergency liquidity, or multiple deadline-constrained goals, and therefore offer only partial support for the broader planning problem considered in this paper.

C. Machine Learning Methods
Machine-learning-based robo-advising goes beyond fixed questionnaires by adapting recommendations from data. Alsabah et al. [3] formulate preference learning as a sequential exploration-exploitation problem, and Wang and Yu [13] combine inverse optimization with deep reinforcement learning to support multi-period investment recommendations. These studies show that advisory systems can personalize decisions from observed behavior instead of relying solely on static profiling. At the same time, their learned objectives remain investment-centric: the personalization signal is derived from portfolio choices and returns rather than from household liquidity, savings adequacy, or goal attainment. The preliminary explainability study in [10] reinforces the importance of transparency in personalized financial advice, but it does not offer strong evidence on long-horizon policy quality or robustness.

D. Reinforcement Learning / Multi-Agent Approaches
Deep reinforcement learning has produced strong results in portfolio management, particularly when the environment is nonlinear or the asset universe changes over time. MAPS [1], the trend-regularized multi-agent method in [6], the multi-asset trading framework in [11], and the risk-aware MASA framework in [12] show that decomposed or multi-agent control can coordinate allocation and risk management under changing market conditions. Betancourt and Chen [2] and Yang [5] further demonstrate that RL can handle dynamic asset universes and direct portfolio optimization without hand-crafted rebalancing rules. Interpretable extensions, including AlphaPortfolio [7] and the XDRL analysis of Guan and Liu [8], attempt to explain learned policies after training. Collectively, these papers establish the relevance of RL for sequential financial decision making, but their state representations remain predominantly market-centric.

E. Identified Research Gap
The missing piece is not another portfolio optimizer; it is an integrated framework that links adaptive policy selection to user-level financial constraints. Portfolio RL studies [1], [2], [5]–[8], [11], [12] optimize market-facing decisions, while robo-advisory and explainability studies [3], [4], [9], [10], [13] focus on suitability, trust, or adoption. Neither strand directly addresses a pipeline in which liquidity risk, savings behavior, and goal progress are first estimated explicitly and then used as inputs to sequential strategy selection. This gap is particularly important in retail financial planning, where advice must be both understandable and responsive to household-level constraints.

F. Positioning of Our Work
Our work takes a hybrid rather than fully end-to-end approach. The implemented system uses specialized analytical agents to estimate risk, goal feasibility, and broad asset allocation, then applies DQN only at the strategy-selection layer. This is more limited than fully learned multi-agent portfolio systems [1], [6], [11], [12], but it is better aligned with the current application because it exposes intermediate financial quantities that can be audited and explained. The framework also differs from prior robo-advisory studies [3], [4], [9], [10], [13] by coupling explanation-oriented outputs with a controlled sequential decision module instead of relying only on preference elicitation or static portfolio mapping. The contribution is therefore an implementation-grounded bridge between rule-based personal-finance analytics and reinforcement-learning-based strategy adaptation.

III. Dataset
The study uses a synthetic financial planning dataset rather than real-world personal finance data. This design choice is motivated by the scarcity of publicly accessible, longitudinal personal finance datasets that include income, expenses, liquid balances, asset allocation, and goal metadata at sufficient granularity. Such data are typically unavailable due to privacy, confidentiality, and regulatory constraints. Synthetic data therefore provide a practical basis for method development while avoiding exposure of identifiable financial records.

Each dataset instance represents a simulated household financial profile defined by six primary attributes: current balance, monthly income, monthly expenses, equity allocation ratio, goal target amount, and goal horizon in months. These attributes are sampled from predefined ranges to create heterogeneous user profiles spanning different savings capacities, liquidity conditions, and investment goals. Table I summarizes the raw dataset attributes and their sampling ranges.

TABLE I
SYNTHETIC DATASET ATTRIBUTES

| Feature | Type | Range | Description | Source |
| ------- | ------ | ------ | -------- | -------- |
| balance | Continuous | 10,000–500,000 | Current investable or liquid balance | Synthetic |
| monthly_income | Continuous | 3,000–30,000 | Monthly income inflow | Synthetic |
| monthly_expenses | Continuous | 2,000–25,000 | Monthly spending obligations | Synthetic |
| equity_ratio | Continuous | 0.2–0.8 | Initial equity allocation share | Synthetic |
| goal_target | Continuous | 50,000–2,000,000 | Financial target amount | Synthetic |
| goal_months_remaining | Integer | 12–240 | Remaining time to goal in months | Synthetic |

The dataset is entirely synthetic for both training and evaluation. No identifiable personal financial records are used in the reinforcement learning experiments reported in this paper. In the deployed system, real user information may be processed at inference time to generate recommendations, but the learned policy described here is trained only on simulated profiles.

From each synthetic profile, the analytical pipeline derives a compact five-dimensional normalized state vector used by the DQN policy. These derived features are not raw dataset fields; rather, they are computed from the synthetic profile and agent outputs before policy selection. Table II describes the derived state representation.

TABLE II
DERIVED RL STATE FEATURES

| State Feature | Range | Derived From | Purpose |
| -------------- | ------ | ------------- | --------- |
| risk_score | [0,1] | runway, stability, savings rate | Encodes short-term financial fragility |
| goal_feasibility | [0,1] | projected goal success probability | Encodes likelihood of reaching target |
| equity_ratio | [0,1] | current allocation | Encodes current portfolio risk posture |
| savings_rate | [0,1] | income and expenses | Encodes monthly surplus behavior |
| runway | [0,1] | balance / expenses, normalized | Encodes emergency liquidity capacity |

All state features are normalized to the interval [0,1] to ensure consistent scaling for the neural network. The state encoder maintains a fixed ordering of these five features across all training and inference operations.

IV. Methodology
The proposed system follows a multi-agent architecture in which specialized components analyze complementary dimensions of a user’s financial situation. The production pipeline retrieves profile, account, transaction, and goal data; computes structured financial metrics; constructs a normalized state vector; selects a strategy action; and generates a natural-language report. The core analytical components are summarized below.

Fig. 1. Integrated system architecture linking structured user data, analytical agents, DQN strategy selection, and language-based reporting.

A. Risk Agent
The Risk Agent estimates cash-flow fragility and liquidity capacity from recent transactions and liquid account balances. In the deployed pipeline, burn rate is computed from recent debit transactions, monthly income is computed from recent credits, and runway is defined as liquid assets divided by monthly burn rate. A normalized risk score is then computed as a weighted combination of runway, stability ratio, and savings ratio: riskscore = 40*normalize(runway) + 30*normalize(stability) + 30*savingsratio, with normalization bounds of 0-12 months for runway and 0.5-2.0 for the stability ratio. The implementation clamps the final score to the range 0-100.

B. Goal Feasibility Agent
The Goal Feasibility Agent estimates whether financial goals are achievable under current savings behavior. For each goal, the system first computes a deterministic future value using current savings, monthly contributions, and an expected annual return of 7%. It then performs 500 Monte Carlo simulations using returns sampled from a Gaussian distribution centered at the expected annual return with standard deviation 0.15. The estimated success probability is the fraction of simulated trajectories that reach or exceed the target amount by the target date. Goals are labeled ontrack when success probability is at least 0.75, atrisk when it is between 0.40 and 0.75, and unrealistic otherwise.

C. Investment Allocation Agent
The Investment Allocation Agent recommends a broad asset-class allocation across equity, debt, cash, and other assets. The allocation is heuristic rather than learned. It combines an age-based baseline equity rule, time-horizon adjustments, average goal pressure, a user risk-appetite modifier, capacity constraints derived from risk score, and a macro-state adjustment. The output always includes a recommended allocation and may include a more aggressive alternative when there is a mismatch between low risk capacity and high stated risk appetite.

D. Strategy Agent
The Strategy Agent is the only learned decision component in the current implementation, although the application can fall back to a heuristic policy when a trained DQN is unavailable. The experimental results reported in this paper correspond to the DQN configuration. The action space has size five: keep strategy, increase savings, reduce savings, shift to equity, and shift to bonds.

The input state is the five-dimensional vector produced by the state encoder. The learning model is a DQN with two hidden fully connected layers of sizes 64 and 32, each followed by ReLU activation, and an output layer over the five actions. The network therefore maps a 5-dimensional normalized financial state to five Q-values.

The reward function in the training environment is rt = 0.01∆W − 2 I(R < 3) + 5 I(G) − 3 I(¬G) (1) where rt denotes the reward at time step t, ∆W represents the change in net worth during the current step, R denotes the financial runway measured in months, and G is a binary indicator representing whether the financial goal is projected to be on track. The indicator function I(·) evaluates to 1 when the condition inside the parentheses is true and 0 otherwise. The term −2 I(R < 3) penalizes states with critically low runway, while +5 I(G) rewards trajectories where goals remain achievable and −3 I(¬G) penalizes states where goals are projected to fail.

This formulation Eq. 1 encourages wealth growth while penalizing short runway and rewarding projected goal attainability. Each environment step corresponds to one simulated month.

E. Explanation Layer
The final component is a language-generation module that converts structured outputs into a human-readable report. In the current implementation, the system can use either an external large language model or a deterministic mock fallback. The explanation layer is not part of the reinforcement learning optimization itself; it operates on structured agent outputs after strategy selection. This design is aligned with work on explainable financial AI, post hoc interpretation of learned policies, and adoption of algorithmic advisors [4], [8]–[10].

V. Experimental Setup

Training is conducted for 3,000 episodes in a synthetic financial environment. At the beginning of each episode, a new financial profile is sampled randomly from the initialization ranges described above. The episode length is randomized between 60 and 120 monthly steps. Thus, the agent is trained on heterogeneous long-horizon trajectories rather than on a single deterministic scenario.

The environment includes dynamic market regimes that transition stochastically between normal, bull, bear, and recession states. Each regime has distinct return distributions: normal markets exhibit 7% annual equity returns with 15% volatility; bull markets show 12% returns with reduced 12% volatility; bear markets experience -5% returns with elevated 20% volatility; and recession conditions produce -15% returns with 25% volatility. Debt returns vary by regime from 3% to 4.5% annually. Additionally, the environment applies income and expense shocks with 5% monthly probability to simulate financial variability. These stochastic regimes and shocks are part of the simulation environment used for training and evaluation; they are not claims of live market forecasting in the deployed application.

The DQN uses a replay buffer with capacity 10,000 and is optimized with Adam at a learning rate of 0.001. The discount factor is gamma = 0.99. Mini-batch size is 32. Exploration follows an epsilon-greedy schedule with initial epsilon 1.0, minimum epsilon 0.05, and multiplicative decay factor 0.995 applied after each episode. The target network is updated every 50 episodes.

The feature vector has five dimensions. The ordered features are risk score, goal feasibility, equity ratio, monthly savings rate, and runway. This ordering must remain consistent between training and inference. The DQN output dimension is also five, corresponding to the discrete action space: keep strategy, increase savings, reduce savings, shift to equity, and shift to bonds.

Reproducibility is supported through seed control. The training script accepts a random seed parameter that controls Python, NumPy, and environment randomness. For the results reported below, a fixed seed of 42 was used for both training and evaluation to ensure reproducibility. The current results represent a single-seed run; multi-seed statistical validation remains future work.

The training configuration is summarized in Table III.

TABLE III
TRAINING CONFIGURATION

| Parameter | Value |
| --------- | ----- |
| Episodes | 3,000 |
| Replay buffer size | 10,000 |
| Batch size | 32 |
| Learning rate | 0.001 |
| Discount factor gamma | 0.99 |
| Initial epsilon | 1.0 |
| Minimum epsilon | 0.05 |
| Epsilon decay | 0.995 |
| Target network update | Every 50 episodes |
| State dimension | 5 |
| Action space | 5 actions |
| Episode length | 60–120 steps |

    VI. Results

The trained agent exhibited a clear progression from exploratory behavior toward more stable policy-driven actions as epsilon decayed from 1.0 to 0.05 over the course of training. Training artifacts are saved as plots and tabular summaries, including PNG and PDF figures, CSV logs, and a JSON metrics summary.

A. Training Performance

Across 3,000 training episodes, the DQN agent demonstrated learning progression as measured by cumulative reward, terminal balance, and goal achievement metrics. The raw episode rewards showed high variance due to stochastic market conditions and random initial states, but the 50-episode moving average revealed a clear upward trend. Table IV summarizes the training performance metrics.

TABLE IV
TRAINING PERFORMANCE SUMMARY (3,000 EPISODES, SEED=42)

| Metric | Value |
| -------- | ------- |
| Mean cumulative reward | 10,935.52 ± 9,016.12 |
| Final 100-episode mean reward | 12,370.65 |
| Mean terminal balance | $1,330,012.86 ± $906,494.85 |
| Final 100-episode terminal balance | $1,456,924.95 |
| Mean goal-feasibility score | 0.732 |
| Final 100-episode goal-feasibility | 0.740 |
| Mean minimum runway | 34.09 months |  
| Low-runway episodes (< 3 months) | 207 / 3,000 (6.9%) |
| Final epsilon | 0.05 |

The improvement from early to late training is evident: the final 100-episode mean reward (12,370.65) represents a 13.1% increase over the overall mean (10,935.52), while the final 100-episode goal-feasibility score (0.740) shows a 1.1% improvement over the overall mean (0.732). These trends indicate that the agent learned to improve financial outcomes over the course of training.

B. Baseline Comparison

To assess the learned policy's effectiveness, we evaluated the trained DQN agent against three baselines on a fixed set of 100 synthetic scenarios:

1. Heuristic baseline: Rule-based strategy that increases savings when runway is low or goal feasibility is poor, shifts to bonds when equity is too high, and shifts to equity when runway is strong and equity is low
2. Keep-strategy baseline: Always selects action 0 (no changes to current strategy)
3. Random baseline: Uniformly random action selection from the five available actions

All agents were evaluated with exploration disabled (epsilon=0) on identical scenarios generated with seed 42 to ensure fair comparison. Table V presents the baseline comparison results.

TABLE V
BASELINE COMPARISON ON 100 EVALUATION SCENARIOS (SEED=42)

| Agent | Mean Reward | Terminal Balance | Goal On-Track Rate | Low Runway Rate |
| ------- | ------------- | ------------------ | ------------------- | ----------------- |
| DQN | 12,186.91 ± 6,540.02 | $1,459,256.51 ± $680,638.06 | 87% | 4% |
| Heuristic | 7,156.81 ± 7,432.11 | $978,677.44 ± $766,204.40 | 57% | 5% |
| Keep | 3,332.25 ± 8,950.35 | $610,579.49 ± $909,436.93 | 31% | 49% |
| Random | 6,723.31 ± 8,529.93 | $931,879.98 ± $891,652.96 | 52% | 5% |

The DQN agent outperformed all baselines across key metrics. Compared to the heuristic baseline, the DQN achieved:
- +70.3% improvement in cumulative reward (12,186.91 vs 7,156.81)
- +49.1% improvement in terminal balance ($1,459,256.51 vs $978,677.44)
- +30 percentage point improvement in goal on-track rate (87% vs 57%)
- Comparable low-runway safety (4% vs 5%)

The DQN's advantage over the keep-strategy and random baselines was even more pronounced, demonstrating that active policy learning provides substantial value over passive or random decision-making in this simulated environment.

C. Policy Behavior Analysis

Qualitatively, the learned policy exhibits financially conservative behavior under stress conditions. When runway falls below critical thresholds or goal feasibility deteriorates, the policy favors increased savings rates and reduced equity exposure. Conversely, when financial stability is strong and equity allocation is low, the policy shifts toward higher-equity positions to maximize long-term growth potential. This adaptive behavior aligns with sound financial planning principles and demonstrates that the reward structure successfully incentivizes prudent decision-making.

    VII. Conclusion

This paper presented a hybrid multi-agent framework for personalized financial planning and asset allocation. The implemented system integrates rule-based risk assessment, simulation-based goal analysis, heuristic asset allocation, a reinforcement-learning strategy layer, and a report-generation layer into a single pipeline. Relative to portfolio-centric RL studies [1], [2], [11], [12], the framework shifts the state representation toward household liquidity, savings behavior, and goal progress.

The experiments show that a compact five-dimensional state representation and a small discrete-action DQN can learn financially meaningful behaviors in a synthetic monthly environment. The reported results concern the DQN variant of the Strategy Agent and come from a single-seed run (seed = 42, 3,000 episodes). Under those conditions, the final 100-episode metrics improved 13.1% in reward and 1.1% in goal feasibility over the overall training means. Evaluation on 100 fixed scenarios showed that the learned DQN policy outperformed heuristic, keep-strategy, and random baselines by substantial margins, including a 70.3% gain in cumulative reward and a 49.1% gain in terminal balance relative to the heuristic baseline.

These findings should be interpreted as controlled simulation evidence rather than validated real-world advisory performance. The experiments rely on synthetic data, a single random seed, and no confidence intervals or statistical significance tests. The contribution of this work is therefore architectural and methodological: it demonstrates that rule-based financial analysis can be coupled with reinforcement learning and auditable artifacts in a reproducible prototype.

The study also underscores the role of interpretability in AI-enabled finance. By generating user-facing explanations from structured agent outputs, the framework moves beyond opaque optimization toward a more transparent decision-support workflow, consistent with prior work on explainable financial AI and robo-advising [4], [8]–[10].

A. Future Work

Several extensions are necessary before the framework can be considered production-grade or scientifically mature. First, future experiments should evaluate multiple runs with different random seeds and report confidence intervals or other statistical uncertainty measures to validate the robustness of the reported performance gains. Second, the environment should be expanded to include richer macroeconomic regimes, transaction costs, inflation, and more sophisticated user behavior models. Third, comparative experiments against stronger baselines, including rule-based planning policies and alternative reinforcement learning algorithms such as PPO or actor-critic methods, would provide a clearer assessment of relative performance.

A further priority is external validity. Because the current experiments rely on synthetic financial data, the model’s real-world effectiveness remains unverified. Future work should evaluate the framework on privacy-preserving or consented real financial datasets, or on carefully curated semi-synthetic benchmarks. In the application layer, the current market-context and language-generation integrations can fall back to mock services; replacing those fallbacks with validated external providers is future engineering work rather than a contribution claimed in this paper. Ethical safeguards must remain central: personal financial data are sensitive, and any deployment should minimize data exposure, use strict user-level access control, and ensure that generated explanations are framed as decision support rather than regulated financial advice.

Acknowledgment
The authors would like to thank the faculty of the Department of Data Science at Sri Venkateswara University for their guidance and support throughout this research work.

References
[1] J. Lee, R. Kim, S.-W. Yi, and J. Kang, “MAPS: Multi-Agent reinforcement learning-based Portfolio management System.” in Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelli- gence. Yokohama, Japan: International Joint Conferences on Artificial Intelligence Organization, Jul. 2020, pp. 4520–4526.
[2] C. Betancourt and W.-H. Chen, “Deep reinforcement learning for portfolio management of markets with a dynamic number of assets,” Expert Systems with Applications, vol. 164, p. 114002, Feb. 2021.
[3] H. Alsabah, A. Capponi, O. R. Lacedelli, and M. Stern, “Robo-advising: Learning Investors’ Risk Preferences via Portfolio Choices,” Journal of Financial Econometrics, vol. 19, no. 2, pp. 369–392, Aug. 2021.
[4] D. Ben David, Y. S. Resheff, and T. Tron, “Explainable AI and Adoption of Financial Algorithmic Advisors: an Experimental Study,” arXiv preprint arXiv:2101.02555, 2021.
[5] S. Yang, “Deep reinforcement learning for portfolio management,”
Knowledge-Based Systems, vol. 278, p. 110905, Oct. 2023.
[6] C. Ma, J. Zhang, Z. Li, and S. Xu, “Multi-agent deep reinforcement learning algorithm with trend consistency regularization for portfolio management,” Neural Computing and Applications, vol. 35, no. 9, pp. 6589–6601, Mar. 2023.
[7] L. W. Cong, K. Tang, J. Wang, and Y. Zhang, “AlphaPortfolio: Direct Construction Through Deep Reinforcement Learning and Interpretable AI,” SSRN Working Paper 3554486, 2021.
[8] M. Guan and X.-Y. Liu, “Explainable Deep Reinforcement Learning for Portfolio Management: An Empirical Approach,” arXiv preprint arXiv:2111.03995, 2021.
[9] M. Bianchi and M. Briere, “Robo-Advising: Less AI and More XAI?” SSRN Working Paper 3825110, 2021.
[10] A. Litty, “Explainable AI for Personalized Financial Advice: Building Trust and Transparency in Robo-Advisory Platforms,” EasyChair Preprint 14333, 2024.
[11] L.-C. Cheng and J.-S. Sun, “Multiagent-based deep reinforcement learning framework for multi-asset adaptive trading and portfolio management,” Neurocomputing, vol. 594, p. 127800, Aug. 2024.
[12] Z. Li, V. Tam, and K. L. Yeung, “Developing A Multi-Agent and Self-Adaptive Framework with Deep Reinforcement Learning for Dynamic Portfolio Risk Management,” arXiv preprint arXiv:2402.00515, 2024.
[13] H. Wang and S. Yu, “Robo-Advising: Enhancing Investment with Inverse Optimization and Deep Reinforcement Learning,” arXiv preprint arXiv:2105.09264, 2021.
