import gymnasium as gym
import numpy as np
from tqdm import tqdm

env = gym.make('LunarLander-v2', render_mode='human')

out_rewards = []
rewards = []

for i in tqdm(range(1000)):

    obs = env.reset(seed=42)[0]
    iter_reward = 0

    while True:
        obs, r, done, terminated, info = env.step(np.random.randint(0,4))
        iter_reward += r

        if done or terminated:
            rewards.append(iter_reward)
            break

    if i != 0 and i % 10 == 0:
        avg_rwd = np.mean(np.array(rewards))
        out_rewards.append(avg_rwd)
        rewards = []

np.savetxt('results/simulation_random.txt', out_rewards)
