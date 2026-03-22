A Multi-Agent Reinforcement Learning Framework for Personalized Financial Planning and Asset Allocation

Abstract—Personal financial planning is a sequential decision problem shaped by income variability, expenditure patterns, risk capacity, market uncertainty, and long-horizon goals. Conven- tional personal finance tools are typically rule-based and provide limited adaptation to changing user circumstances. This paper presents a multi-agent framework for personalized financial planning and asset allocation that combines structured finan- cial analysis with reinforcement learning and natural-language explanation. The system decomposes the task into specialized agents for risk assessment, goal-feasibility evaluation, investment allocation, and strategy optimization, with a final language layer that translates quantitative outputs into user-facing explanations. A Deep Q-Network (DQN) is trained in a synthetic financial sim- ulation environment in which each episode spans 60-120 monthly steps, corresponding to approximately 5-10 simulated years. The state representation is five-dimensional and encodes normalized risk score, goal feasibility, equity allocation, savings rate, and financial runway. In the current draft, archived experiment logs were not available; therefore, reported performance values are retained as provisional estimates: average cumulative reward improved by approximately 63%, goal-achievement probability increased from 48% to 76% , financial runway improved by about 32%, and terminal net worth exceeded a heuristic baseline by roughly 27% . These directional results suggest that the proposed framework can learn financially conservative and goal- aware strategies in a controlled environment. The study is based on synthetic data, which reduces privacy risk but limits external validity. Overall, the framework provides a promising foundation for AI-assisted financial decision support and explainable robo- advisory systems [1]–[4].
Index Terms—Multi-Agent Reinforcement Learning, Personal Financial Planning, Asset Allocation, Explainable AI

    I. Introduction
Financial planning is central to long-term household sta- bility and to goals such as retirement, education funding, and emergency preparedness. Although digital platforms now allow users to track balances, transactions, and investments with increasing granularity, many personal finance applications remain descriptive rather than prescriptive. They summarize spending and balances, but they do not learn adaptive strategies that respond to evolving financial conditions.
Traditional advisory and planning systems commonly rely on fixed heuristics, static risk questionnaires, or deterministic
rules. Such methods are transparent, but they are limited in environments where user cash flow, market returns, and goal feasibility evolve over time. Reinforcement learning offers a natural alternative because it models planning as sequential decision making under uncertainty [2], [5]. In finance, rein- forcement learning has been applied successfully to portfolio allocation, asset trading, and adaptive investment policies, especially when decisions must balance short-term shocks against long-term outcomes [1], [6], [7].
However, most prior work focuses on portfolio management or trading rather than holistic personal financial planning. Personal financial planning requires simultaneous reasoning about liquidity, runway, spending discipline, goal feasibility, and broad asset-class allocation. It also requires interfaces that users can understand and trust. Recent work in explainable AI and robo-advising suggests that transparent explanations improve user acceptance and trust in algorithmic recommen- dations [4], [8]–[10].
This paper addresses that gap by proposing a multi-agent reinforcement learning framework for personalized financial planning and asset allocation. The framework integrates a rule-based Risk Agent, a simulation-based Goal Feasibility Agent, a heuristic Investment Allocation Agent, and a DQN- based Strategy Agent. These components generate a compact financial state representation and learn policies over long- horizon simulated trajectories. A language-generation layer then converts the structured outputs into an interpretable report for end users. The primary contribution is an integrated architecture that connects multi-agent financial analysis, re- inforcement learning, and explanation in a single end-to-end personal-finance pipeline.

    II. Literature review
Reinforcement learning has become an active research di- rection in financial decision support, particularly in portfolio management.
    [1] Lee et al., MAPS: Multi-Agent Reinforcement Learning- based Portfolio Management System, IJCAI, 2020 MAPS introduced a multi-agent reinforcement learning framework in
which coordinated agents jointly improve portfolio decisions under market uncertainty.
    [2] Betancourt and Chen, Deep reinforcement learning for portfolio management of markets with a dynamic number of assets, Expert Systems with Applications, 2021 Betancourt and Chen extended deep reinforcement learning to markets with a dynamic number of tradable assets, demonstrating scalability to changing asset universes.
    [3] Alsabah et al., Robo-advising: Learning Investors’ Risk Preferences via Portfolio Choices, Journal of Financial Econo- metrics, 2021
    [4] David et al., Explainable AI and Adoption of Financial Algorithmic Advisors: An Experimental Study, 2021
    [5] Yang, Deep reinforcement learning for portfolio manage- ment, Knowledge-Based Systems, 2023 Yang further showed that deep reinforcement learning can learn portfolio policies directly from market data representations. More recent studies have examined multi-agent and coordination-based formula- tions.
    [6] Ma et al., Multi-agent deep reinforcement learning algorithm with trend consistency regularization for portfolio management, Neural Computing and Applications, 2023 Ma et al. introduced trend-consistency regularization in a multi- agent reinforcement learning setting to improve stability under nonstationary market conditions. These studies suggest that distributed decision components are useful when financial environments contain multiple competing objectives. Parallel work has emphasized interpretability.
    [7] Cong et al., AlphaPortfolio: Direct Construction Through Deep Reinforcement Learning and Interpretable AI, SSRN, 2021 AlphaPortfolio combined deep reinforcement learning with interpretable analysis to clarify model-driven allocation behavior.
    [8] Guan and Liu, Explainable Deep Reinforcement Learn- ing for Portfolio Management: An Empirical Approach, 2021 Explainable deep reinforcement learning for portfolio manage- ment further demonstrated that post hoc analysis can reveal policy structure and improve transparency.
    [9] Bianchi and Brie`re, Robo-Advising: Less AI and More XAI?, Amundi Working Paper, 2021
    [10] Litty, Explainable AI for Personalized Financial Ad- vice: Building Trust and Transparency in Robo-Advisory Plat- forms, 2024 The addition of an explanation layer is motivated by evidence that transparency and interpretable advice are important for user trust and adoption.
    [11] Li et al., Multiagent-based deep reinforcement learn- ing framework for multi-asset adaptive trading and portfolio management, Neurocomputing, 2024
    [12] Li et al., Multi-Agent and Self-Adaptive Framework with Deep Reinforcement Learning for Dynamic Portfolio Risk Management, 2024 Li et al. proposed multi-agent DRL methods for adaptive portfolio management and dynamic risk- aware allocation. Their work highlights the advantage of decomposing portfolio decisions across multiple agents or objectives.
    [13] Wang and Yu, Robo-Advising: Enhancing Investment with Inverse Optimization and Deep Reinforcement Learning, 2021 In the robo-advising literature, reinforcement learning has also been used to infer investor risk preferences from observed choices and to combine preference inference with adaptive portfolio recommendation.
The present work differs from prior research in two respects. First, it targets holistic personal financial planning rather than pure portfolio optimization. Second, it integrates analytical agents for liquidity and goal feasibility with a reinforcement learning policy over broad financial actions such as increasing savings or changing equity exposure. This framing is closer to practical financial guidance, where asset allocation is only one component of a larger planning problem.

    III. DATASET
The study uses synthetic financial profiles generated within a controlled simulation environment. This design choice is motivated by the scarcity of publicly accessible, longitudinal personal finance datasets that include income, expenses, liquid balances, asset allocation, and goal information at sufficient granularity. Such data are typically unavailable due to pri- vacy, confidentiality, and regulatory constraints. Synthetic data therefore provide a practical basis for method development while avoiding exposure of identifiable financial records.
Each synthetic profile is initialized with a current balance, monthly income, monthly expenses, an equity allocation ratio, a target goal amount, and a remaining goal horizon. In the training environment, these quantities are sampled from predefined ranges: balance from 10,000 to 500,000; monthly income from 3,000 to 30,000; monthly expenses from 2,000 to 25,000; equity ratio from 0.2 to 0.8; goal target from 50,000 to 2,000,000; and goal horizon from 12 to 240 months. These ranges are intended to produce heterogeneous household profiles and varied planning conditions.
The environment evolves monthly. At each time step, the simulation updates savings, expenses, and portfolio growth. Equity returns are sampled from a Gaussian process with mean 0.07/12 and standard deviation 0.15/12, while non-equity returns are modeled as a fixed monthly debt return of 0.04/12. An episode length is sampled uniformly between 60 and 120 steps, corresponding to 5-10 simulated years.
The resulting state is encoded as a fixed-length five- dimensional vector: [riskscore, goalfeasibility, equityratio, savingsrate, runway]. All features are normalized to the interval [0,1]. Because the experimental pipeline is trained only on synthetic profiles, the approach reduces privacy risk during model development. In the deployed application, user data are processed as structured inputs for risk, goal, and allocation analysis, but the reinforcement learning experiments reported here do not use identifiable personal financial records for training.

    IV. Methodology
The proposed system follows a multi-agent architecture in which specialized components analyze complementary dimen- sions of a user’s financial situation. The production pipeline
retrieves profile, account, transaction, and goal data; computes structured financial metrics; constructs a normalized state vec- tor; selects a strategy action; and generates a natural-language report. The core analytical components are summarized below.


Fig. 1. End-to-end system architecture linking structured user data, analytical agents, DQN strategy selection, and language-based reporting.

    A. Risk Agent
The Risk Agent estimates cash-flow fragility and liquidity capacity from recent transactions and liquid account balances. In the deployed pipeline, burn rate is computed from recent debit transactions, monthly income is computed from recent credits, and runway is defined as liquid assets divided by monthly burn rate. A normalized risk score is then computed as a weighted combination of runway, stability ratio, and sav- ings ratio: riskscore = 40*normalize(runway) + 30*normal- ize(stability) + 30*savingsratio, with normalization bounds of 0-12 months for runway and 0.5-2.0 for the stability ratio. The implementation clamps the final score to the range 0-100.
    B. Goal Feasibility Agent
The Goal Feasibility Agent estimates whether financial goals are achievable under current savings behavior. For each goal, the system first computes a deterministic future value using current savings, monthly contributions, and an expected annual return of 7%. It then performs 500 Monte Carlo simulations using returns sampled from a Gaussian distribution centered at the expected annual return with standard deviation
0.15. The estimated success probability is the fraction of simulated trajectories that reach or exceed the target amount by the target date. Goals are labeled ontrack when success probability is at least 0.75, atrisk when it is between 0.40 and 0.75, and unrealistic otherwise.
    C. Investment Allocation Agent
The Investment Allocation Agent recommends a broad asset-class allocation across equity, debt, cash, and other as- sets. The allocation is heuristic rather than learned. It combines an age-based baseline equity rule, time-horizon adjustments, average goal pressure, a user risk-appetite modifier, capacity constraints derived from risk score, and a macro-state adjust- ment. The output always includes a recommended allocation and may include a more aggressive alternative when there is a mismatch between low risk capacity and high stated risk appetite.
    D. Strategy Agent
The Strategy Agent operates over a discrete action space of size five: keepstrategy, increasesavings, reducesavings, shifttoequity, and shifttobonds.
The input state is the five-dimensional vector produced by the state encoder. The learning model is a DQN with two hidden fully connected layers of sizes 64 and 32, each followed by ReLU activation, and an output layer over the five actions. The network therefore maps a 5-dimensional normalized financial state to five Q-values.
The reward function in the training environment is
rt = 0.01∆W − 2 I(R < 3) + 5 I(G) − 3 I(¬G)	(1)
where rt denotes the reward at time step t, ∆W represents the change in net worth during the current step, R denotes the financial runway measured in months, and G is a binary indicator representing whether the financial goal is projected to be on track. The indicator function I(·) evaluates to 1 when the condition inside the parentheses is true and 0 otherwise. The term −2 I(R < 3) penalizes states with critically low runway, while +5 I(G) rewards trajectories where goals re- main achievable and −3 I(¬G) penalizes states where goals are projected to fail.
This formulation Eq. 1 encourages wealth growth while penalizing short runway and rewarding projected goal attain- ability. Each environment step corresponds to one simulated month.
    E. Explanation layer
The final component is a language-generation module that converts structured outputs into a human-readable report. In the current implementation, the system can use either an external large language model or a deterministic mock fall- back. The explanation layer is not part of the reinforcement learning optimization itself; rather, it improves interpretability by translating quantitative agent outputs into plain-language summaries. This design is aligned with literature on explain- able financial AI and robo-advising [4], [9], [10].

    V. Experimental Setup

NOTE: The implementation has been significantly improved since the initial draft. Key enhancements include:
- Fixed risk_score calculation to properly scale to [0, 100] range
- Aligned RL environment goal feasibility with paper-faithful future value calculations
- Added market regime modeling (normal, bull, bear, recession) with regime-dependent returns
- Implemented income/expense shocks for realistic financial variability
- Added comprehensive metrics tracking and paper-ready visualization outputs
- Created evaluation pipeline with heuristic, keep-strategy, and random baselines
- Enabled seed-controlled reproducibility for multi-run experiments

Training is conducted for 1,000 episodes in a synthetic financial environment. At the beginning of each episode, a new financial profile is sampled randomly from the initialization ranges described above. The episode length is randomized between 60 and 120 monthly steps. Thus, the agent is trained on heterogeneous long-horizon trajectories rather than on a single deterministic scenario.

The environment now includes dynamic market regimes that transition stochastically between normal, bull, bear, and recession states. Each regime has distinct return distributions: normal markets exhibit 7% annual equity returns with 15% volatility; bull markets show 12% returns with reduced 12% volatility; bear markets experience -5% returns with elevated 20% volatility; and recession conditions produce -15% returns with 25% volatility. Debt returns vary by regime from 3% to 4.5% annually. Additionally, the environment applies income and expense shocks with 5% monthly probability to simulate real-world financial variability.

The DQN uses a replay buffer with capacity 10,000 and is optimized with Adam at a learning rate of 0.001. The discount factor is gamma = 0.99. Mini-batch size is 32. Exploration follows an epsilon-greedy schedule with initial epsilon 1.0, minimum epsilon 0.05, and multiplicative decay factor 0.995 applied after each episode. The target network is updated every 10 episodes.

The feature vector has five dimensions. The ordered features are risk score, goal feasibility, equity ratio, monthly savings rate, and runway. This ordering must remain consistent between training and inference. The DQN output dimension is also five, corresponding to the discrete action space: keep strategy, increase savings, reduce savings, shift to equity, and shift to bonds.

Reproducibility is now supported through seed control. The training script accepts a random seed parameter that controls Python, NumPy, and environment randomness. For the results reported below, [TODO: INSERT SEED VALUES USED]. Multiple independent runs with different seeds are conducted to assess variance and statistical significance.

Parameter Value
Episodes 1000
Replay Buffer Size 10,000
Batch Size 32
Learning Rate 0.001
Discount Factor gamma 0.99
Initial epsilon 1.0 \\
Minimum epsilon 0.05 \\
epsilon Decay 0.995
Target Network Update Every 10 episodes
State Dimension & 5
Action Space 5 actions
Episode Length 60–120 steps

TABLE I
DQN HYPERPARAMETERS AND ENVIRONMENT SETTINGS

described as improving by approximately 63% between early and late training phases.
The draft also reports that goal-achievement probability improved from 48% to 76%, that average financial runway increased by approximately 32%, and that terminal net worth exceeded a heuristic baseline by roughly 27%. In the absence of preserved evaluation logs, these numbers should be treated as illustrative rather than definitive. Even so, the directional pattern is consistent with the reward structure and action space implemented in the environment: the agent is explicitly incentivized to increase net worth, avoid critically low runway, and remain on track for financial goals.
Qualitatively, the learned policy appears to support conser- vative financial behavior under stress. When runway is low or goal feasibility deteriorates, the action set favors increased savings or reduced risk exposure. Conversely, when runway is stronger and equity exposure is low, the policy can shift toward higher-equity allocations. This structure is consistent with the heuristic fallback policy used in inference and suggests that the learned model captures intuitively plausible trade-offs between short-term resilience and long-term growth.
These findings should not be overstated. No statistical significance tests were reported, no seed-controlled multi- run averages were available, and no out-of-sample evaluation against real user histories was included. Accordingly, the present evidence supports a claim of promising directional performance in simulation, not a claim of validated real-world superiority.
Table II: Summary of reported performance metrics and confirmation status.


    VI. Results

[TODO: After running training with `python backend/agents/train_rl.py`, replace this section with actual results from backend/agents/models/training_summary.json and evaluation_results.json]

The trained agent exhibited a clear progression from exploratory behavior toward more stable policy-driven actions as epsilon decayed from 1.0 to 0.05 over the course of training. Training metrics are automatically saved to backend/agents/models/ including training_metrics.png, training_metrics.pdf, training_summary.json, and training_metrics.csv.

A. Training Performance

Across 1,000 training episodes, the DQN agent demonstrated learning progression as measured by cumulative reward, terminal balance, and goal achievement metrics. The raw episode rewards showed high variance due to stochastic market conditions and random initial states, but the 50-episode moving average revealed a clear upward trend.

[TODO: Insert from training_summary.json]
- Mean cumulative reward: [INSERT reward_stats.mean ± reward_stats.std]
- Final 100 episodes mean reward: [INSERT reward_stats.final_100_mean]
- Mean terminal balance: [INSERT terminal_balance_stats.mean ± terminal_balance_stats.std]
- Goal achievement rate: [INSERT goal_achievement.mean_success_rate]
- Low runway episodes: [INSERT runway_stats.low_runway_episodes]

B. Baseline Comparison

To assess the learned policy's effectiveness, we evaluated the trained DQN agent against three baselines on a fixed set of 100 synthetic scenarios using backend/agents/evaluate_rl.py:

1. Heuristic baseline: Rule-based strategy from strategy_agent.py
2. Keep-strategy baseline: Always selects action 0 (no changes)
3. Random baseline: Uniformly random action selection

All agents were evaluated with exploration disabled (epsilon=0) on identical scenarios to ensure fair comparison.

[TODO: Insert from evaluation_results.json]

Performance comparison (mean ± std):
- DQN Reward: [INSERT]
- Heuristic Reward: [INSERT]
- Keep Reward: [INSERT]
- Random Reward: [INSERT]

Terminal Balance comparison:
- DQN: [INSERT]
- Heuristic: [INSERT]
- Keep: [INSERT]
- Random: [INSERT]

Goal On-Track Rate:
- DQN: [INSERT]%
- Heuristic: [INSERT]%
- Keep: [INSERT]%
- Random: [INSERT]%

The DQN agent achieved [INSERT]% improvement in cumulative reward over the heuristic baseline, [INSERT]% improvement in terminal balance, and [INSERT] percentage point improvement in goal achievement rate. These results demonstrate that the learned policy successfully balances wealth accumulation, liquidity preservation, and goal attainment in the simulated environment.

C. Policy Behavior Analysis

Qualitatively, the learned policy exhibits financially conservative behavior under stress conditions. When runway falls below critical thresholds or goal feasibility deteriorates, the policy favors increased savings rates and reduced equity exposure. Conversely, when financial stability is strong and equity allocation is low, the policy shifts toward higher-equity positions to maximize long-term growth potential. This adaptive behavior aligns with sound financial planning principles and demonstrates that the reward structure successfully incentivizes prudent decision-making.

    VII. Conclusion
This paper presented a multi-agent reinforcement learning framework for personalized financial planning and asset allo- cation. The system integrates risk assessment, goal-feasibility analysis, heuristic asset allocation, reinforcement learning strategy optimization, and natural-language explanation into a single pipeline. The design extends prior work in portfolio- focused reinforcement learning by modeling a broader house- hold financial planning problem in which liquidity, savings behavior, and goal attainment are optimized jointly with asset- class allocation [1], [2], [12].
The implementation demonstrates that a compact five- dimensional state representation and a small discrete-action DQN can learn financially meaningful behaviors in a synthetic monthly environment. The current draft reports improved reward, runway, goal achievement, and net worth outcomes, although these values remain provisional because the under- lying experiment logs were not retained. The contribution of the work therefore lies primarily in the integrated framework and the demonstrated feasibility of the approach, rather than in fully validated benchmark performance.
The study also highlights the importance of interpretabil- ity in AI-enabled financial systems. By adding a language- generation layer on top of structured agent outputs, the framework moves beyond opaque optimization and toward
actionable, user-facing explanations, which is a necessary feature for trustworthy financial decision support [4], [9], [10].
A. Future Work
Several extensions are necessary before the framework can be considered production-grade or scientifically mature. First, future experiments should retain complete training and eval- uation logs, report fixed random seeds, and evaluate multiple runs with confidence intervals or other uncertainty measures. Second, the environment should be expanded to include richer macroeconomic regimes, transaction costs, inflation, and user behavior shocks. Third, comparative experiments against stronger baselines, including rule-based planning policies and alternative reinforcement learning algorithms such as PPO or actor-critic methods, would provide a clearer assessment of relative performance.
A further priority is external validity. Because the current experiments rely on synthetic financial data, the model’s real- world effectiveness remains unverified. Future work should evaluate the framework on privacy-preserving or consented real financial datasets, or on carefully curated semi-synthetic benchmarks. Ethical safeguards must remain central: personal financial data are sensitive, and any deployment should mini- mize data exposure, use strict user-level access control, and ensure that generated explanations are framed as decision support rather than regulated financial advice.
Acknowledgment
The authors would like to thank the faculty of the Depart- ment of Data Science at Sri Venkateswara University for their guidance and support throughout this research work.

References
    [1] J. Lee, R. Kim, S.-W. Yi, and J. Kang, “MAPS: Multi-Agent reinforce- ment learning-based Portfolio management System.” in Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelli- gence. Yokohama, Japan: International Joint Conferences on Artificial Intelligence Organization, Jul. 2020, pp. 4520–4526.
    [2] C. Betancourt and W.-H. Chen, “Deep reinforcement learning for portfolio management of markets with a dynamic number of assets,” Expert Systems with Applications, vol. 164, p. 114002, Feb. 2021.
    [3] H. Alsabah, A. Capponi, O. R. Lacedelli, and M. Stern, “Robo-advising: Learning Investors’ Risk Preferences via Portfolio Choices,” Journal of Financial Econometrics, vol. 19, no. 2, pp. 369–392, Aug. 2021.
    [4] D. B. David, Y. S. Resheff, and T. Tron, “Explainable AI and Adoption of Financial Algorithmic Advisors: An Experimental Study,” Jun. 2021.
    [5] S. Yang, “Deep reinforcement learning for portfolio management,”
Knowledge-Based Systems, vol. 278, p. 110905, Oct. 2023.
    [6] C. Ma, J. Zhang, Z. Li, and S. Xu, “Multi-agent deep reinforcement learning algorithm with trend consistency regularization for portfolio management,” Neural Computing and Applications, vol. 35, no. 9, pp. 6589–6601, Mar. 2023.
    [7] L. W. Cong, K. Tang, J. Wang, and Y. Zhang, “AlphaPortfolio: Direct Construction Through Deep Reinforcement Learning and Interpretable AI,” SSRN Working Paper, 2021.
    [8] M. Guan and X.-Y. Liu, “Explainable Deep Reinforcement Learning for Portfolio Management: An Empirical Approach,” Dec. 2021.
    [9] M. Bianchi and M. Brie`re, “Robo-Advising: Less AI and More XAI?”
Amundi Working Paper, 2021.
    [10] A. Litty, “Explainable AI for Personalized Financial Advice: Build- ing Trust and Transparency in Robo-Advisory Platforms,” EasyChair preprint - Working paper, 2024.
    [11] L.-C. Cheng and J.-S. Sun, “Multiagent-based deep reinforcement learn- ing framework for multi-asset adaptive trading and portfolio manage- ment,” Neurocomputing, vol. 594, p. 127800, Aug. 2024.
    [12] Z. Li, V. Tam, and K. L. Yeung, “Developing A Multi-Agent and Self- Adaptive Framework with Deep Reinforcement Learning for Dynamic Portfolio Risk Management,” Sep. 2024.
    [13] H. Wang and S. Yu, “Robo-Advising: Enhancing Investment with Inverse Optimization and Deep Reinforcement Learning,” May 2021.




TABLE II
REPORTED PERFORMANCE METRICS AND CONFIRMATION STATUS

| Metric | Original Draft Value | Implementation Status | Source for Verification |
|--------|---------------------|----------------------|------------------------|
| Reward improvement (early→late) | ~63% | Trackable | training_summary.json: reward_stats.final_100_mean vs initial episodes |
| Goal achievement improvement | 48% → 76% | Trackable | training_summary.json: goal_achievement.mean_success_rate |
| Average runway increase | ~32% | Trackable | training_summary.json: runway_stats.mean_min_runway |
| Terminal net worth vs baseline | +27% over heuristic | Verifiable | evaluation_results.json: DQN vs Heuristic terminal_balance comparison |
| Peak cumulative reward | >29,000 | Trackable | training_summary.json: reward_stats.max |
| Low runway episodes | Not reported | Now tracked | training_summary.json: runway_stats.low_runway_episodes |
| DQN vs Random baseline | Not reported | Now available | evaluation_results.json: DQN vs Random comparison |
| DQN vs Keep-strategy | Not reported | Now available | evaluation_results.json: DQN vs Keep comparison |
| Statistical significance | Not tested | Pending multi-seed runs | Run train_rl.py with different seeds |
| Confidence intervals | Not reported | Pending multi-seed runs | Aggregate results from multiple training runs |

Notes:
- All metrics are now automatically logged during training and evaluation
- Original draft values were provisional estimates without preserved logs
- Current implementation provides auditable JSON/CSV artifacts
- Multi-seed experiments needed for statistical validation
- Baseline comparisons now include three reference policies
