import subprocess
import simulate_dqn
from tqdm import tqdm
import numpy as np
"""
process = subprocess.Popen(['python', 'DQN_plan.py'], shell=False)
process.wait()

process = subprocess.Popen(['python', 'DQN_plan_v2.py'], shell=False)
process.wait()

process = subprocess.Popen(['python', 'DQN_naive.py'], shell=False)
process.wait()
"""

sim_results = []
for i in tqdm(range(10), leave=False):
    process = subprocess.Popen(['python', 'DQN_naive.py'], shell=False)
    process.wait()
    sim_results.append(simulate_dqn.main('naive400x80'))
np.savetxt('saved_models/avg_sim_naive400x80.txt', sim_results)