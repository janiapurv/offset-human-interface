import yaml
from pathlib import Path
import time

import ray

from server.parameters import ParameterServer
from envs.environments import Benning
from gui.main import MainGUI

from utils import skip_run

config_path = Path(__file__).parents[1] / 'offset-game/config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)

with skip_run('run', 'Game Test') as check, check():

    # Initiate ray
    if not ray.is_initialized():
        ray.init(num_cpus=4)

    # Instantiate parameter server
    ps = ParameterServer.remote()

    # Instantiate environment
    env = Benning.remote(config)

    # Instantiate GUI
    gui = MainGUI.remote((1500, 750), ps)

    start_time = time.time()
    for i in range(10):
        gui.run.remote(ps)
        env_run_id = env.step.remote(ps)
        env_reset_id = env.reset.remote(ps)
        ray.get([env_run_id, env_reset_id])

    # Shutdown ray
    ray.shutdown()
