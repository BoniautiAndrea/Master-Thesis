# File to run a simulation in lunar lander with the learned policy.
# Now it is only for tabular RL
import argparse
import json
import numpy as np
import gymnasium as gym
from sarsa import discretize_Q
from collections import defaultdict
from tqdm import tqdm

ACTION_DICT = {
    'idle' : 0,
    'right_engine' : 1,
    'main_engine' : 2,
    'left_engine' : 3,
    'goal' : 0
}

def state_extractor(s):
    state = (min(3, max(-3, int((s[0]) / 0.05))), \
            min(3, max(-1, int((s[1]) / 0.1))), \
            min(2, max(-2, int((s[2]) / 0.1))), \
            min(2, max(-2, int((s[3]) / 0.1))), \
            min(2, max(-2, int((s[4]) / 0.1))), \
            min(2, max(-2, int((s[5]) / 0.1))), \
            int(s[6]), \
            int(s[7]))

    return state

def sa_key(s, a):
    return str(s) + " " + str(a)

def policy_explorer(s, Q):
    Qv = np.array([ Q[sa_key(s, action)] for action in [0, 1, 2, 3]])
    return np.argmax(Qv)

def find_action(state, policy):
    actions = []
    for i in range(4):
        key = str(state) + f" {i}"
        if key in policy.keys():
            actions.append(policy[str(state) + f" {i}"])
    if actions != []:
        return np.argmax(actions), 0
    else:
        return np.random.randint(0,4), 1
    
def find_action_init(state, policy):
    key = str(state)
    if key in policy.keys():
        action = np.argmax(policy[key])
        return action, 0
    else:
        return np.random.randint(0,4), 1

def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("path", help="path to the learned policy to use")
    return argparser.parse_args()

def main():

    args = parse_args()
    path = args.path
    with open(f'results/{path}', 'r') as f:
        policy = json.load(f)

    policy = defaultdict(float, policy)

    env = gym.make('LunarLander-v2', render_mode='human')

    not_found = 0
    rewards = []
    for i in tqdm(range(10)):
        iter_rewards = 0
        obs = env.reset()[0] #[0, 15, 34, 42, 99]
        state = discretize_Q(obs)

        while True:
            action, random = find_action(state, policy)
            if random:
                not_found += 1
            obs, r, done, terminated, info = env.step(action)

            state = discretize_Q(obs)
            iter_rewards += r

            if done or terminated:
                rewards.append(iter_rewards)
                break

    name = path[:-5]
    np.savetxt(f"results/simulation_{name}.txt", rewards)
    avg = np.mean(rewards)
    print(f'States not found: {not_found}')
    print(f'Avg reward: {avg}')

if __name__ == "__main__":
    main()