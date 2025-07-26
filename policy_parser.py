# A little different from the cfond-asp solution, here the resulting policy
# of each domain is a union of multiple runs with different initial states
# and the result is in the policy.out file so we need just the variable parsing
# from the output.sas.
import json
import pickle
import os
import numpy as np
import random

ACTION_DICT = {
    'idle' : 0,
    'right_engine' : 1,
    'main_engine' : 2,
    'left_engine' : 3,
    'goal' : 0
}

class Rule:
    def __init__(self, action = None, x = None, y = None, vx = None, 
                 vy = None, t = None, vt = None):
        self.action = action
        if x != None:
            self.x = str(x)
        else:
            self.x = x
        if y != None:
            self.y = str(y)
        else:
            self.y = y
        if vx != None:
            self.vx = str(vx)
        else:
            self.vx = vx
        if vy != None:
            self.vy = str(vy)
        else:
            self.vy = vy
        if t != None:
            self.t = str(t)
        else:
            self.t = t
        if vt != None:
            self.vt = str(vt)
        else:
            self.vt = vt

    def __str__(self):
        return "State: x={0}, y={1}, t={2}, vx={3}, vy={4}, vt={5}; Action: {6}".format(
            self.x, self.y, self.t, self.vx, self.vy, self.vt, self.action)

    # the self rule will be always the actual rule, while oher the value from observation
    def __eq__(self, other):
        if isinstance(other, Rule):
            if self.x != None and other.x != None:
                if self.x.startswith('not'):
                    if self.x[4:] == other.x:
                        return False
                elif self.x != other.x:
                    return False
            if self.y != None and other.y != None:
                if self.y.startswith('not'):
                    if self.y[4:] == other.y:
                        return False
                elif self.y != other.y:
                    return False
            if self.t != None and other.t != None:
                if self.t.startswith('not'):
                    if self.t[4:] == other.t:
                        return False
                elif self.t != other.t:
                    return False
            if self.vx != None and other.vx != None:
                if self.vx.startswith('not'):
                    if self.vx[4:] == other.vx:
                        return False
                elif self.vx != other.vx:
                    return False
            if self.vy != None and other.vy != None:
                if self.vy.startswith('not'):
                    if self.vy[4:] == other.vy:
                        return False
                elif self.vy != other.vy:
                    return False
            if self.vt != None and other.vt != None:
                if self.vt.startswith('not'):
                    if self.vt[4:] == other.vt:
                        return False
                elif self.vt != other.vt:
                    return False
        return True

    def set_value(self, value: str):
        index = value.find('(')
        specs = value[index+1:-1].split('_')
        if specs[0] == 'x':
            if value.startswith('Atom'):
                self.x = specs[1]
            else:
                self.x = f'not {specs[1]}'
        if specs[0] == 'y':
            if value.startswith('Atom'):
                self.y = specs[1]
            else:
                self.y = f'not {specs[1]}'
        if specs[0] == 't':
            if value.startswith('Atom'):
                self.t = specs[1]
            else:
                self.t = f'not {specs[1]}'
        if specs[0] == 'vx':
            if value.startswith('Atom'):
                self.vx = specs[1]
            else:
                self.vx = f'not {specs[1]}'
        if specs[0] == 'vy':
            if value.startswith('Atom'):
                self.vy = specs[1]
            else:
                self.vy = f'not {specs[1]}'
        if specs[0] == 'vt':
            if value.startswith('Atom'):
                self.vt = specs[1]
            else:
                self.vt = f'not {specs[1]}'

    def listed_rule(self):
        return [self.x, self.y, self.vx, self.vy, self.t, self.vt]

# path should be just the folder, then go to path/output.sas
def get_variables(path):
    with open(f'domains/{path}/output.sas', 'r') as f:
        lines = f.readlines()
    start_indices = [i for i, x in enumerate(lines) if x.strip().startswith('begin_variable')]
    end_indices = [i for i, x in enumerate(lines) if x.strip().startswith('end_variable')]
    indices = list(zip(start_indices, end_indices))
    variables = {}
    for start, end in indices:
        values = []
        for line in lines[start+1:end]:
            if line.startswith('var'):
                name = str(line)[:-1]
            if line.startswith('Atom') or line.startswith('NegatedAtom'):
             values.append(str(line)[:-1])
        variables[name] = values
    return variables

# path should be just the folder, then go to path/policy.out
def parse_policy(path, variables, custom = False):
    if custom:
        full_path = f'{path}/policy.out'
        pkl_path = f'{path}/custom_policy.pkl'
        json_path = f'{path}/custom_policy.json'
    else:
        full_path = f'domains/{path}/policy.txt'
        pkl_path = f'domains/{path}/policy.pkl'
        json_path = f'domains/{path}/policy.json'
    with open(full_path, 'r') as f:
        lines = f.readlines()
    rules = []
    for i in range(len(lines)):
        if lines[i].startswith('If'):
            rule = Rule()
            for couple in lines[i].split(' ')[2:]:
                variable = couple.split(':')
                atom = variables[variable[0]][int(variable[1])]
                rule.set_value(atom)
            action = lines[i+1].split(' ')[1]
            rule.action = action
            if rule not in rules:
                rules.append(rule)

    with open(pkl_path, 'wb') as f:
        pickle.dump(rules, f)
    with open(json_path, 'w') as f:
        json.dump(rules, f, default=lambda o: o.__dict__, indent=4)
    print('Policy parsed and saved..')
    return rules

def get_policy(path, custom = False):
    if not custom:
        full_path = f'domains/{path}/policy.pkl'
    else:
        full_path = f'domains/{path}/custom_policy.pkl'
    if os.path.exists(full_path) and custom == False:
        with open(full_path, 'rb') as f:
            rules = pickle.load(f)
    else:
        variables = get_variables(path)
        rules = parse_policy(path, variables, custom)

    return rules

def discretize_no_x(obs, rule = True):
    values = obs[:6]
    # y
    if values[1] < 0.05:
        values[1] = 0
    elif values[1] < 0.25: #1.3
        values[1] = 1
    else:
        values[1] = 2
    # vy
    if values[3] > 1: #0.05
        values[3] = 1
    elif values[3] > -0.1:
        values[3] = 0
    elif values[3] > -0.3:
        values[3] = -1
    else:
        values[3] = -2
    # t and vt
    for i in [4,5]:
        if values[i] < -0.15:
            values[i] = -1
        elif values[i] < 0.15:
            values[i] = 0
        else:
            values[i] = 1

    if rule:           
        return Rule(x=None, y=int(values[1]), vx=None, vy=int(values[3]), t=int(values[4]), vt=int(values[5]))
    else:
        return (int(values[0]), int(values[1]), int(values[2]), None, int(values[4]), int(values[5]))
    
def discretize_x_only(obs, rule = True):
    values = []
    if obs[0] < -0.25:
        values.append(-2)
    elif obs[0] < -0.15:
        values.append(-1)
    elif obs[0] < 0.15:
        values.append(0)
    elif obs[0] < 0.25:
        values.append(1)
    else:
        values.append(2)
    if obs[2] < -0.25:
        values.append(-2)
    elif obs[2] < -0.15:
        values.append(-1)
    elif obs[2] < 0.15:
        values.append(0)
    elif obs[2] < 0.25:
        values.append(1)
    else:
        values.append(2)
    if rule:           
        return Rule(x=int(values[0]), y=None, vx=int(values[1]), vy=None, t=None, vt=None)
    else:
        return (int(values[0]), None, int(values[2]), None, None, None)
    
def discretize_y_only(obs, rule = True):
    values = []
    if obs[1] < -0.1:
        values.append(-1)
    elif obs[1] < 0.05:
        values.append(0)
    elif obs[1] < 0.3:
        values.append(1)
    elif obs[1] < 0.7:
        values.append(2)
    else:
        values.append(3)
    if obs[3] < -0.7:
        values.append(-3)
    elif obs[3] < -0.4:
        values.append(-2)
    elif obs[3] < -0.15:
        values.append(-1)
    elif obs[3] < 0.05:
        values.append(0)
    else:
        values.append(1)
    if rule:           
        return Rule(x=None, y=int(values[0]), vx=None, vy=int(values[1]), t=None, vt=None)
    else:
        return (None, int(values[0]), None, int(values[2]), None, None)
    
def discretize_t_only(obs, rule = True):
    values = []
    if obs[4] < -0.25:
        values.append(-2)
    elif obs[4] < -0.15:
        values.append(-1)
    elif obs[4] < 0.15:
        values.append(0)
    elif obs[4] < 0.25:
        values.append(1)
    else:
        values.append(2)
    if obs[5] < -0.25:
        values.append(-2)
    elif obs[5] < -0.15:
        values.append(-1)
    elif obs[5] < 0.15:
        values.append(0)
    elif obs[5] < 0.25:
        values.append(1)
    else:
        values.append(2)
    if rule:           
        return Rule(x=None, y=None, vx=None, vy=None, t=int(values[0]), vt=int(values[1]))
    else:
        return (None, None, None, None, int(values[0]), int(values[2]))

def discretize_no_t(obs, rule = True):
    values = obs[:6]
    # y
    if values[1] <= 0.05:
        values[1] = 0
    elif values[1] < 1.3:
        values[1] = 1
    else:
        values[1] = 2
    # vy
    if values[3] > 0.05:
        values[3] = 1
    elif values[3] > -0.1:
        values[3] = 0
    elif values[3] > -0.3:
        values[3] = -1
    else:
        values[3] = -2
    # x, t and vt
    for i in [0,2]:
        if values[i] < -0.15:
            values[i] = -1
        elif values[i] < 0.15:
            values[i] = 0
        else:
            values[i] = 1

    if rule:           
        return Rule(x=int(values[0]), y=int(values[1]), vx=int(values[2]), vy=int(values[3]), t=None, vt=None)
    else:
        return (int(values[0]), int(values[1]), int(values[2]), None, int(values[4]), int(values[5]))

def discretize_domain(obs, rule = True):
    values = obs[:6]
    if values[0] < -0.25:
        values[0] = -1
    elif values[0] < 0.25:
        values[0] = 0
    else:
        values[0] = 1
    # y
    if values[1] <= 0.05:
        values[1] = 0
    elif values[1] < 1.3:
        values[1] = 1
    else:
        values[1] = 2
    # vy
    if values[3] > 0.05:
        values[3] = 1
    elif values[3] > -0.1:
        values[3] = 0
    elif values[3] > -0.3:
        values[3] = -1
    else:
        values[3] = -2
    # x, t and vt
    for i in [4, 5]:
        if values[i] < -0.1:
            values[i] = -1
        elif values[i] < 0.1:
            values[i] = 0
        else:
            values[i] = 1

    if rule:           
        return Rule(x=int(values[0]), y=int(values[1]), vx=None, vy=int(values[3]), t=int(values[4]), vt=int(values[5]))
    else:
        return (int(values[0]), int(values[1]), int(values[2]), None, int(values[4]), int(values[5]))

def discretize_simplified(obs, rule = True):
    # x = [-3, -2, -1, 0, 1, 2, 3]
    # y = [-1, 0, 1, 2, 3]
    # t = [-2, -1, 0, 1, 2]
    # vx = [-2, -1, 0, 1, 2]
    # vy = [-2, -1, 0, 1]
    # vt = [-2, -1, 0, 1, 2]
    values = obs[:6]
    for i,v in enumerate(values):
        # if vx, vy, t or vt
        if i in [2, 3, 4, 5]:
            if v < -0.7:
                values[i] = -2
            elif v < -0.15:
                values[i] = -1
            elif v < 0.15:
                values[i] = 0
            elif i == 3:
                values[i] = 1
            elif v < 0.7:
                values[i] = 1
            else:
                values[i] = 2
        # if x
        elif i == 0:
            if v < -0.7:
                values[i] = -3
            elif v < -0.4:
                values[i] = -2
            elif v < -0.15:
                values[i] = -1
            elif v < 0.15:
                values[i] = 0
            elif v < 0.4:
                values[i] = 1
            elif v < 0.7:
                values[i] = 2
            else:
                values[i] = 3
        # if y
        else:
            if v < -0.15:
                values[i] = -1
            elif v < 0.15:
                values[i] = 0
            elif v < 0.6:
                values[i] = 1
            elif v < 1.1:
                values[i] = 2
            else:
                values[i] = 3
    if rule:           
        return Rule(x=int(values[0]), y=int(values[1]), vx=int(values[2]), vy=int(values[3]), t=int(values[4]), vt=int(values[5]))
    else:
        return (int(values[0]), int(values[1]), int(values[2]), int(values[3]), int(values[4]), int(values[5]))

def discretize_mini(obs, rule = True):
    # x = [-1, 0, 1]
    # y = [0, 1, 2]
    # t = [-1, 0, 1]
    # vx = [-1, 0, 1]
    # vy = [-2, -1, 0, 1]
    # vt = [-1, 0, 1]
    values = obs[:6]
    # x value
    if values[0] > 0.4:
        values[0] = 1
    elif values[0] < -0.4:
        values[0] = -1
    else:
        values[0] = 0
    # y value
    if values[1] > 1.1:
        values[1] = 2
    elif values[1] < 0.6:
        values[1] = 0
    else:
        values[1] = 1
    # other values
    for i,v in enumerate(values):
        if i in [2, 4, 5]:
            if v > 0.15:
                values[i] = 1
            elif v < -0.15:
                values[i] = -1
            else:
                values[i] = 0
        elif i == 3:
            if v > 0.1:
                values[i] = 1
            elif v > -0.15:
                values[i] = 0
            elif v > -0.7:
                values[i] = -1
            else:
                values[i] = -2
    if rule:
        return Rule(x=int(values[0]), y=int(values[1]), vx=int(values[2]), vy=int(values[3]), t=int(values[4]), vt=int(values[5]))
    else:
        return (int(values[0]), int(values[1]), int(values[2]), int(values[3]), int(values[4]), int(values[5]))
   
def from_disc_mini(state):
    for i, s in enumerate(state):
        if s is not None and s.startswith('not'):
            value = int(s[4:])
            if i == 0:
                if value == -1:
                    state[i] = random.uniform(-0.4, 1.3)
                elif value == 1:
                    state[i] = random.uniform(-1.3, 0.4)
                else:
                    state[i] = random.choice([-1, 1]) * random.uniform(0.4, 1.3)
            elif i == 1:
                if value == 0:
                    state[i] = random.uniform(0.6, 1.5)
                elif value == 2:
                    state[i] = random.uniform(0., 1.1)
                else:
                    state[i] = random.uniform(0., 0.6) if random.choice([-1,1]) == -1 else random.uniform(1.1, 1.5)
            elif i == 3:
                if value == -2:
                    state[i] = random.uniform(-0.7, 0.3)
                elif value == 1:
                    state[i] = random.uniform(-1.5, 0.1)
                elif value == -1:
                    state[i] = random.uniform(-1.5, -0.7) if random.choice([-1,1]) == -1 else random.uniform(-0.15, 0.5)
                else:
                    state[i] = random.uniform(-1.5, -0.2) if random.choice([-1,1]) == -1 else random.uniform(0.1, 1)
            else:
                if value == -1:
                    state[i] = random.uniform(-0.1, 1)
                elif value == 1:
                    state[i] = random.uniform(-1, -0.1)
                else:
                    state[i] = random.uniform(-1, -0.2) if random.choice([-1,1]) == -1 else random.uniform(0.2, 1)
        elif s is not None:
            if i == 0:
                if s == -1:
                    state[i] = random.uniform(-1.3, -0.4)
                elif s == 1:
                    state[i] = random.uniform(0.4, 1.3)
                else:
                    state[i] = random.uniform(-0.4, 0.4)
            elif i == 1:
                if s == 2:
                    state[i] = random.uniform(1.1, 1.5)
                elif s == 1:
                    state[i] = random.uniform(0.6, 1.1)
                else:
                    state[i] = random.uniform(0., 0.6)
            elif i == 3:
                if s == -2:
                    state[i] = random.uniform(-1.5, -0.7)
                elif s == 1:
                    state[i] = random.uniform(0.1, 0.5)
                elif s == -1:
                    state[i] = random.uniform(-0.7, -0.2)
                else:
                    state[i] = random.uniform(-0.15, 0.1)
            else:
                if s == 1:
                    state[i] = random.uniform(0.15, 1)
                elif s == -1:
                    state[i] = random.uniform(-1, -0.15)
                else:
                    state[i] = random.uniform(-0.15, 0.15)
        
    #obs = [random.uniform(-1, 1, step=0.1) if s in None else state[i] for i, s in enumerate(state)]
    for i, s in enumerate(state):
        if s is None:
            state[i] = random.uniform(-1, 1)
    return state

def discretize_novelocity(obs, rule = True):
    # x = {-10, 10}
    # y = {-1, 10}
    # t = {-4, 4}
    values = [obs[0], obs[1], obs[4]]
    # t
    if values[2] < -1.2:
        values[2] = -4
    elif values[2] < -0.8:
        values[2] = -3
    elif values[2] < -0.4:
        values[2] = -2
    elif values[2] < -0.10:
        values[2] = -1
    elif values[2] < 0.10:
        values[2] = 0
    elif values[2] < 0.4:
        values[2] = 1
    elif values[2] < 0.8:
        values[2] = 2
    elif values[2] < 1.2:
        values[2] = 3
    else:
        values[2] = 4
    # x and y
    for i in [0,1]:
        if i == 1 and values[i] < 0.05:
            if values[i] < -0.05:
                values[i] = -1
            else:
                values[i] = 0
        elif i == 0 and abs(values[i]) < 0.1:
            values[i] = 0
        elif values[i] > 0:
            values[i] = np.ceil(6.66*values[i])
        else:
            values[i] = np.floor(6.66*values[i])
        if values[i] > 10:
            values[i] = 10
        if values[i] < -10:
            values[i] = -10
    if rule:
        return Rule(x=int(values[0]), y=int(values[1]), t=int(values[2]))
    else:
        return (int(values[0]), int(values[1]), int(values[2]))

def from_discretize(state, domain):
    if domain == 'mini':
        return from_disc_mini(state)
    else:
        return None

def get_action_by_model(observation, model, policy):
    print(f'Observation: {observation[:6]}')
    if model == 'mini':
        state = discretize_mini(observation)
    elif model == 'simplified':
        state = discretize_simplified(observation)
    else:
        state = discretize_novelocity(observation)
    print(f'State discretized = {state}')
    for rule in policy:
        if rule == state:
            print(f'Rule found, action {rule.action} selected..')
            return rule.action
    relaxed_state = Rule(x=state.x, y=state.y, t=state.t)
    rules = []
    for rule in policy:
        if rule == relaxed_state:
            rules.append(rule)
    if len(rules) > 0:
        action = random.choice(rules).action
        print(f'Rule found for the relaxed state, action {rule.action} selected..')
        return rule.action
    print('No rule found for this state.. returning idle action')
    return 'idle'

def get_action(state, policy):
    for rule in policy:
        if rule == state:
            return rule.action
    #print("Unexpected search, rule not found, returning Idle action..")
    #return random.choice(['idle', 'main_engine', 'left_engine', 'right_engine'])
    return -1
    #return 'idle'

# simple method for checking if a state (already in a Rule object) is present in the policy
def find_state(state, policy):
    for rule in policy:
        if rule == state:
            return True
    return False

def action_from_combined(obs, policies):
    plan_x, plan_y, plan_t = policies
    action = [0,0,0,0]
    state_disc = discretize_x_only(obs)
    if find_state(state_disc, plan_x):
        action[ACTION_DICT[get_action(state_disc, plan_x)]] += 1
    state_disc = discretize_y_only(obs)
    if find_state(state_disc, plan_y):
        action[ACTION_DICT[get_action(state_disc, plan_y)]] += 1
    state_disc = discretize_t_only(obs)
    if find_state(state_disc, plan_t):
        action[ACTION_DICT[get_action(state_disc, plan_t)]] += 1
    if np.max(action) != 0:
        if np.max(action[1:]) in [2,3]:
            return np.argmax(action)
        else:
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

def discretize_Q(s):
    state = (min(5, max(-5, int((s[0]) / 0.05))), \
            min(5, max(-1, int((s[1]) / 0.1))), \
            min(3, max(-3, int((s[2]) / 0.1))), \
            min(3, max(-3, int((s[3]) / 0.1))), \
            min(3, max(-3, int((s[4]) / 0.1))), \
            min(3, max(-3, int((s[5]) / 0.1))), \
            int(s[6]), \
            int(s[7]))

    return state
