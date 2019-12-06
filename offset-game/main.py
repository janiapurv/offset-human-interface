import yaml
from pathlib import Path
import time

import ray

from server.parameters import ParameterServer
from envs.environments import Benning
from complexity.environments import ComplexBenning
from gui.main import MainGUI

from utils import skip_run

config_path = Path(__file__).parents[1] / 'offset-game/config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)

with skip_run('skip', 'Game Test') as check, check():

    # Initiate ray
    if not ray.is_initialized():
        ray.init(num_cpus=4)

    # Instantiate parameter server
    ps = ParameterServer.remote(config)

    # Instantiate environment
    env = Benning.remote(config)

    # Instantiate GUI
    gui = MainGUI.remote(config, (1500, 750), ps)

    gui_run_id = gui.run.remote(ps)
    env_run_id = env.step.remote(ps)
    ray.wait([env_run_id, gui_run_id])
    print(time.time() - ray.get(gui.get_start_time.remote()))

    # Shutdown ray
    ray.shutdown()

with skip_run('run', 'Complexity Test') as check, check():

    # Initiate ray
    if not ray.is_initialized():
        ray.init(num_cpus=4)

    # Instantiate parameter server
    ps = ParameterServer.remote(config)

    # Instantiate complex environment
    complex_env = ComplexBenning.remote(config)

    # Instantiate environment
    env = Benning.remote(config)

    # Instantiate GUI
    gui = MainGUI.remote(config, (1500, 750), ps)

    # Get the remote IDs
    gui_run_id = gui.run.remote(ps)
    env_run_id = env.step.remote(ps)
    complex_run_id = complex_env.step.remote(ps)

    # Run the simulation
    ray.wait([complex_run_id, env_run_id, gui_run_id])
    print(time.time() - ray.get(gui.get_start_time.remote()))

    # Shutdown ray
    ray.shutdown()
