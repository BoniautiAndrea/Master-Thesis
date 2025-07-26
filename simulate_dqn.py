import torch
import numpy as np
import gymnasium as gym
from tqdm import tqdm
from DQN_plan import DQN

def main(version):

    model = DQN(8, 4)
    model.load_state_dict(torch.load(f'saved_models/{version}.pt'))
    model.eval()

    env = gym.make('LunarLander-v2', render_mode='rgb_array') # rgb_array human
    #steps = []
    rewards = []
    for i in tqdm(range(100)):
        iter_rewards = 0
        obs = env.reset()[0] #[0, 15, 34, 42, 99]
        steps_done = 0
        while True:
            with torch.no_grad():
                actions = model(torch.tensor(obs, requires_grad=False))
            action = np.argmax(actions.detach().numpy())
            obs, r, done, terminated, info = env.step(action)
            #steps_done += 1
            iter_rewards += r

            if done or terminated or steps_done > 750:
                rewards.append(iter_rewards)
                #steps.append(steps_done)
                break

    #np.savetxt(f"results/sim_init_trained_100test.txt", rewards)
    avg = np.mean(rewards)
    print(f'Avg reward: {avg}')
    #steps_avg = np.mean(steps)
    #print(f'Steps avg: {steps_avg}')
    return avg

if __name__ == "__main__":
    main('dqn_plan_it583')
    #main('plan_v1')
    #main('plan_v2')