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
    ps = ParameterServer.remote(config)

    # Instantiate environment
    env = Benning.remote(config)

    # Instantiate GUI
    gui = MainGUI.remote(config, (1500, 750), ps)

    start_time = time.time()
    gui_run_id = gui.run.remote(ps)
    env_run_id = env.step.remote(ps)
    ray.get([env_run_id])
    print(time.time() - start_time)

    # Shutdown ray
    ray.shutdown()
