import time
import yaml
from pathlib import Path

import numpy as np
import pybullet as p
import matplotlib.pyplot as plt

from envs.environments import Benning
from envs.utils import get_xy_position

# from models.torch_network import Actor, Critic
# from models.torch_train import AdvantageCritic

from utils import skip_run

# The configuration file
config_path = Path(__file__).parents[1] / 'offset-game/config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)

with skip_run('run', 'learning tactic') as check, check():

    env = Benning(config)
    # ['n_robots', 'primitive', 'target_node_id', 0, 0, 0]
    net_output_1 = [[20, 1, 38, 0, 0, 0], [10, 1, 39, 0, 0, 0],
                    [20, 1, 40, 0, 0, 0], [12, 1, 15, 0, 0, 0],
                    [9, 1, 12, 0, 0, 0], [4, 1, 11, 0, 0, 0]]
    start = time.time()
    for j in range(1):
        print(j)
        _, _, done = env.step(net_output_1)
        if done:
            break
    print(time.time() - start)