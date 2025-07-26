import policy_parser as pp
import gymnasium as gym
from tqdm import tqdm
import numpy as np

ACTION_DICT = {
    'idle' : 0,
    'right_engine' : 1,
    'main_engine' : 2,
    'left_engine' : 3,
    'goal' : 0
}

def action_from_combined(obs, policies):
    plan_x, plan_y, plan_t = policies
    action = [0,0,0,0]
    state_disc = pp.discretize_x_only(obs)
    if pp.find_state(state_disc, plan_x):
        action[ACTION_DICT[pp.get_action(state_disc, plan_x)]] += 1
    state_disc = pp.discretize_y_only(obs)
    if pp.find_state(state_disc, plan_y):
        action[ACTION_DICT[pp.get_action(state_disc, plan_y)]] += 1
    state_disc = pp.discretize_t_only(obs)
    if pp.find_state(state_disc, plan_t):
        action[ACTION_DICT[pp.get_action(state_disc, plan_t)]] += 1
    if np.max(action) != 0:
        if np.max(action[1:]) in [2,3]:
            return np.argmax(action)
        else:
            #actions_found = [a for a in range(4) if action[a] == 1]
            #if actions_found == []:
            #    return 0
            #else:
            #    return np.random.choice(actions_found)
            
            #if action[1] == 1 and action[3] == 1:
            #    return np.random.choice([1,3])
            if action[2] == 1:
                return 2
            if action[1] == 1:
                return 1
            if action[3] == 1:
                return 3
            else:
                return 0
            
    else:
        return -1
    
def action_from_two(obs, policies):
    plan_no_x, plan_no_t = policies
    action = [0,0,0,0]
    state_disc = pp.discretize_no_x(obs)
    if pp.find_state(state_disc, plan_no_x):
        action[ACTION_DICT[pp.get_action(state_disc, plan_no_x)]] += 1
    state_disc = pp.discretize_no_t(obs)
    if pp.find_state(state_disc, plan_no_t):
        action[ACTION_DICT[pp.get_action(state_disc, plan_no_t)]] += 1
    if np.max(action) != 0:
        #print(f'Actions: {action}')
        if np.max(action) == 2:
            return np.argmax(action)
        else:
            while True:
                rand = np.random.choice([0,1,2,3])
                if action[rand] == 1:
                    return rand
    else:
        return -1

plans = 'three'
#policy = pp.get_policy('no_x')
if plans == 'three':
    plan_x = pp.get_policy('x_only')
    plan_y = pp.get_policy('y_only')
    plan_t = pp.get_policy('t_only')
    policies = (plan_x, plan_y, plan_t)
if plans == 'two':
    plan_no_x = pp.get_policy('no_x')
    plan_no_t = pp.get_policy('no_t')
    policies = (plan_no_x, plan_no_t)
else:
    policy = pp.get_policy('no_x_v2')

env = gym.make('LunarLander-v2', render_mode='rgb_array')

rewards = []
out_rewards = []
found = 0
num_states = 0
missing_states = []

for i in tqdm(range(100)):
    obs = env.reset()[0]
    iter_rewards = 0
    #state = pp.discretize_no_x(obs)
    while True:
        #action = ACTION_DICT[pp.get_action(state, policy)]
        if plans == 'three':
            action = pp.action_from_combined(obs, policies)
        elif plans == 'two':
            action = action_from_two(obs, policies)
        else:
            state_disc = pp.discretize_no_x(obs)
            if pp.find_state(state_disc, policy):
                action = ACTION_DICT[pp.get_action(state_disc, policy)]
        if action != -1:
            obs, r, done, terminated, info = env.step(action)
            found += 1
        else:
            #missing_states.append(obs[:6].tolist())
            #print(missing_states[-1])
            obs, r, done, terminated, info = env.step(np.random.choice([0,1,2,3]))
            
        num_states += 1

        iter_rewards += r
        #state = pp.discretize_no_x(obs)

        if done or terminated:
                rewards.append(iter_rewards)
                break
        
    if i != 0 and i % 10 == 0:
         avg_rwd = np.mean(np.array(rewards))
         out_rewards.append(avg_rwd)
         rewards = []

name = 'combined_new'
print(np.mean(out_rewards))
#np.savetxt(f"results/simulation_plan_{name}.txt", out_rewards)
print(f'Total states: {num_states}')
print(f'Found states: {found}')
#print(f'Missing states: {missing_states}')
