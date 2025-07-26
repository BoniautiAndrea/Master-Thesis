import os
import json
import gymnasium as gym
from tqdm import tqdm
import policy_parser as pp
import numpy as np

with open('results/tabular_init_combined_Q.json', 'r') as f:
    policy = json.load(f)

with open('domains/combined/init_Q.json', 'r') as f:
    plan = json.load(f)

env = gym.make('LunarLander-v2', render_mode='rgb_array')

right = 0
wrong = 0
total = 0

for step in tqdm(range(100)):
    obs = env.reset()[0]

    while True:
        d_state = str(pp.discretize_Q(obs))
        if d_state in policy.keys():
            action_policy = np.argmax(policy[d_state])
        else:
            action_policy = -1
        if d_state in plan.keys():
            action_plan = np.argmax(plan[d_state])
        else:
            action_plan = -1

        if action_plan != -1 and action_policy != -1:
            obs, r, done, _, info = env.step(np.random.choice([action_policy, action_plan]))
            if action_plan == action_policy:
                right += 1
            else:
                wrong += 1
            total += 1
        else:
            obs, r, done, _, info = env.step(np.random.choice([0,1,2,3]))

        if done:
            break

print(f'Total states: {total}')
print(f'Correct: {right}')
print(f'Wrong: {wrong}')
print(f'With a perc. of: {right/total}')
print(f'Stati plan: {len(plan.keys())}')
print(f'Stati policy: {len(policy.keys())}')
