import numpy as np
import matplotlib.pyplot as plt

with open('saved_models/dqn_plan_it583_rewards.txt', 'r') as f:
    plan_dqn = np.array(f.readlines(), dtype=float)
with open('saved_models/baseline_it716_rewards.txt') as f:
    baseline = np.array(f.readlines(), dtype=float)

def moving_average(data_set, periods=3):
    weights = np.ones(periods) / periods
    return np.convolve(data_set, weights, mode='valid')

plan_dqn_ma = moving_average(plan_dqn,30)
baseline_ma = moving_average(baseline, 30)

x = np.linspace(0, 716, baseline.shape[0])
plt.plot(x, baseline, 'b', label=f'classic DQN')
x = np.linspace(0, 583, plan_dqn.shape[0])
plt.plot(x, plan_dqn, 'r', label=f'plan + dqn')

plt.legend()
plt.savefig('plots/dqn_baseline_vs_plan_learning_precise.png')
