import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import gymnasium as gym
import numpy as np
from collections import namedtuple, deque
import random
import math
from itertools import count
from tqdm import tqdm
import policy_parser as pp
import json
import os
import sys

ACTION_DICT = {
    'idle' : 0,
    'left_engine' : 1,
    'main_engine' : 2,
    'right_engine' : 3,
    'goal' : 0
}

# if GPU is to be used
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# BATCH_SIZE is the number of transitions sampled from the replay buffer
# GAMMA is the discount factor as mentioned in the previous section
# EPS_START is the starting value of epsilon
# EPS_END is the final value of epsilon
# EPS_DECAY controls the rate of exponential decay of epsilon, higher means a slower decay
# TAU is the update rate of the target network
# LR is the learning rate of the ``AdamW`` optimizer
BATCH_SIZE = 64
GAMMA = 0.99
EPS_START = 0.9
EPS_END = 0.01
EPS_DECAY = 0.99#1000 60
epsilon = 1
TAU = 0.005
LR = 1e-4
TARGET_R = 200
PATH = 'saved_models/'
MEM_SIZE = 10000

def random_sample_from_policy(policy, domain):
    rule = random.choice(policy)
    state = rule.listed_rule()
    state = pp.from_discretize(state, domain)
    state.append(0)
    state.append(0)
    action = ACTION_DICT[rule.action]
    return state, action

def random_sample_from_policy_json(policy, domain):
    key = random.choice(list(policy.keys()))
    action = np.argmax(policy[key])
    key = str.split(key[1:-1], ', ')
    state = []
    state.append(int(key[0])*0.05 + np.random.random()*0.01)
    for i in key[1:-2]:
        state.append(int(i)*0.1 + np.random.random()*0.001)
    state.append(int(key[-2]))
    state.append(int(key[-1]))
    return state, action

def get_policy_json(domain):
    with open(f'domains/{domain}/init_Q.json', 'r') as f:
        policy = json.load(f)
    return policy

def train_plan(policy, domain, iter, batch_size):
    if os.path.exists('saved_models/init.pt'):
        policy_net.load_state_dict(torch.load('saved_models/init.pt'))
        return
    else:
        train_loss = 0
        prog_bar = tqdm(range(iter), desc='Init iter:')
        for it in prog_bar:
            batch = []
            targets = []
            for b in range(batch_size):
                state, action = random_sample_from_policy_json(policy, domain)
                batch.append(state)
                target = [0., 0., 0., 0.]
                target[action] = 100.
                targets.append(target)
            batch = torch.tensor(batch)
            targets = torch.tensor(targets)

            optimizer.zero_grad()
            preds = policy_net(batch)
            criterion = nn.SmoothL1Loss()
            loss = criterion(preds, targets)
            train_loss += loss
            loss.backward()
            #torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
            optimizer.step()
            if it % 100 == 0 and it != 0:
                prog_bar.set_postfix_str(f'loss: {train_loss.item()/100}')
                train_loss = 0

Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))

class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)
    
class DQN(nn.Module):

    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, 128)
        self.layer2 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, n_actions)

    # Called with either one element to determine next action, or a batch
    # during optimization. Returns tensor([[left0exp,right0exp]...]).
    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)
    
def select_action(state, init, episode):
    sample = random.random()
    """
    if init:
        eps_threshold = max(0.05, 0.5 - (0.5*episode/100))
    else:
        eps_threshold = EPS_END + (EPS_START - EPS_END) * \
            math.exp(-1. * episode / EPS_DECAY)
    """
    if sample > epsilon:
        with torch.no_grad():
            # t.max(1) will return the largest column value of each row.
            # second column on max result is index of where max element was
            # found, so we pick action with the larger expected reward.
            return policy_net(state).max(1).indices.view(1, 1)
    else:
        if episode < 100 and init == False:
            return torch.tensor([[pp.action_from_combined(state.detach().numpy()[0], (plan_x, plan_y, plan_t))]], device='cpu', dtype=torch.long)
        else:
            return torch.tensor([[env.action_space.sample()]], device='cpu', dtype=torch.long) #device=device

def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    # This converts batch-array of Transitions to Transition of batch-arrays.
    batch = Transition(*zip(*transitions))

    # Compute a mask of non-final states and concatenate the batch elements
    # (a final state would've been the one after which simulation ended)
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                          batch.next_state)), device='cpu', dtype=torch.bool) # device=device
    non_final_next_states = torch.cat([s for s in batch.next_state
                                                if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
    # columns of actions taken. These are the actions which would've been taken
    # for each batch state according to policy_net
    state_action_values = policy_net(state_batch).gather(1, action_batch)

    # Compute V(s_{t+1}) for all next states.
    # Expected values of actions for non_final_next_states are computed based
    # on the "older" target_net; selecting their best reward with max(1).values
    # This is merged based on the mask, such that we'll have either the expected
    # state value or 0 in case the state was final.
    next_state_values = torch.zeros(BATCH_SIZE, device='cpu') # device=device
    with torch.no_grad():
        next_state_values[non_final_mask] = target_net(non_final_next_states).max(1).values
    # Compute the expected Q values
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # Compute Huber loss
    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    # In-place gradient clipping
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()
    global epsilon
    if epsilon > EPS_END:
        epsilon *= EPS_DECAY

if __name__ == '__main__':

    init = True

    env = gym.make('LunarLander-v2', render_mode='rgb_array')
    # Get number of actions from gym action space
    n_actions = env.action_space.n
    # Get the number of state observations
    state, info = env.reset()
    n_observations = len(state)

    # Define PDDL domain and get its policy
    print('Importing plan..')
    domain = 'combined'
    if init:
        policy = get_policy_json(domain)
    else:
        plan_x = pp.get_policy('x_only')
        plan_y = pp.get_policy('y_only')
        plan_t = pp.get_policy('t_only')

    # Define network and initialize it qith the PDDL plan
    policy_net = DQN(n_observations, n_actions)#.to(device)
    optimizer = optim.AdamW(policy_net.parameters(), lr=0.05, amsgrad=True)
    if init:
        print('Starting initialization pretraining..')
        train_plan(policy, domain, 100, BATCH_SIZE)
        print('Pretraining done..')
        torch.save(policy_net.state_dict(), f'{PATH}init_100.pt')
        
    target_net = DQN(n_observations, n_actions)#.to(device)
    target_net.load_state_dict(policy_net.state_dict())

    optimizer = optim.AdamW(policy_net.parameters(), lr=LR, amsgrad=True)
    memory = ReplayMemory(10000)

    num_episodes = 1000
    episode_rewards = []

    print('Starting training..')
    training_loop = tqdm(range(num_episodes), desc='Ep.: ', leave=False)
    for i_episode in training_loop:
        # Initialize the environment
        reward_sum = 0
        state, info = env.reset()
        state = torch.tensor(state, dtype=torch.float32, device='cpu').unsqueeze(0) # device=device
        for steps in count():
            action = select_action(state, init, i_episode)
            observation, reward, terminated, truncated, _ = env.step(action.item())
            reward_sum += reward
            reward = torch.tensor([reward], device='cpu') #device=device
            done = terminated or truncated

            if done:
                next_state = None
            else:
                next_state = torch.tensor(observation, dtype=torch.float32, device='cpu').unsqueeze(0) # device=device

            # Store the transition in memory
            memory.push(state, action, next_state, reward)

            # Move to the next state
            state = next_state

            # Perform one step of the optimization (on the policy network)
            optimize_model()

            # Soft update of the target network's weights
            # θ′ ← τ θ + (1 −τ )θ′
            target_net_state_dict = target_net.state_dict()
            policy_net_state_dict = policy_net.state_dict()
            for key in policy_net_state_dict:
                target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)
            target_net.load_state_dict(target_net_state_dict)

            if done or steps > 1000:
                episode_rewards.append(reward_sum)
                training_loop.set_postfix_str(f'R: {episode_rewards[-1]}')
                break
        if len(episode_rewards) >= 100 and np.mean(episode_rewards[-100:]) > TARGET_R:
            print(f'Lunar Lander solved.. at episode {i_episode}')
            torch.save(policy_net.state_dict(), f'{PATH}dqn_initplan_it{i_episode}.pt')
            np.savetxt(f'{PATH}/dqn_initplan_it{i_episode}_rewards.txt', episode_rewards)
            break
            
    print('Done..')

    #torch.save(policy_net.state_dict(), f'{PATH}plan_v1.pt')
    #np.savetxt(f'{PATH}/eps40/dqn_plan_v1.txt', episode_rewards)
