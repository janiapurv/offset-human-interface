import yaml
from pathlib import Path
import collections

import ray


@ray.remote
class ParameterServer(object):
    def __init__(self, config):
        self.uav = []
        self.ugv = []
        self.grid_map = []
        self.config = config
        self.actions = collections.defaultdict(dict)
        self.states = collections.defaultdict(dict)

        # Parameters for pausing and resuming the game
        self.pause = False
        self.resume = True

        # Perforn initial setup
        self._initial_setup()
        return None

    def _initial_setup(self):
        # Read fields for all the platoons
        read_path = Path(__file__).parents[0] / 'parameters.yml'
        parameters = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

        # Setup the uav platoons
        for i in range(self.config['simulation']['n_uav_platoons']):
            uav_parameters = parameters['uav'].copy()
            key = 'uav_p_' + str(i + 1)
            uav_parameters['platoon_id'] = i + 1
            self.actions['uav'][key] = uav_parameters

        # Setup the uav platoons
        for i in range(self.config['simulation']['n_ugv_platoons']):
            ugv_parameters = parameters['ugv'].copy()
            key = 'ugv_p_' + str(i + 1)
            ugv_parameters['platoon_id'] = i + 1
            self.actions['ugv'][key] = ugv_parameters

    def set_game_state(self, state):
        if state == 'pause':
            self.pause = True
            self.resume = False
        else:
            self.pause = False
            self.resume = True
        return None

    def get_game_state(self):
        game_state = {'pause': self.pause, 'resume': self.resume}
        return game_state

    def get_actions(self):
        return self.actions

    def set_actions(self, actions):
        vehicle_type = actions['vehicles_type']
        key = vehicle_type + '_p_' + str(actions['platoon_id'])
        self.actions[vehicle_type][key] = actions
        return None

    def update_actions(self, actions_uav, actions_ugv):
        self.actions['uav'] = actions_uav
        self.actions['ugv'] = actions_ugv
        return None

    def set_states(self, uav, ugv, grid_map):
        self.uav = uav
        self.ugv = ugv
        self.map = grid_map
        self.states = {'uav': self.uav, 'ugv': self.ugv, 'map': self.grid_map}
        return None

    def get_states(self):
        self.states = {'uav': self.uav, 'ugv': self.ugv, 'map': self.grid_map}
        return self.states
