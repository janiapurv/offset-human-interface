import yaml
from pathlib import Path
import time

import ray

from server.parameters import ParameterServer
from envs.environments import Benning
# from gui.main import MainGUI

from utils import skip_run

# The configuration file
config_path = Path(__file__).parents[1] / 'offset-game/config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)

with skip_run('run', 'Environment test') as check, check():

    # Initiate ray
    if not ray.is_initialized():
        ray.init(num_cpus=4)

    # Instantiate parameter server
    ps = ParameterServer.remote()

    # Instantiate environment
    env = Benning.remote(config)

    start_time = time.time()
    for j in range(10):
        print(j)
        env_run_id = env.step.remote(ps)
        env_reset_id = env.reset.remote(ps)
        ray.get([env_run_id, env_reset_id])
        print(time.time() - start_time)

    # Shutdown ray
    ray.shutdown()

with skip_run('skip', 'Parameter server test') as check, check():
    print('Hello')
