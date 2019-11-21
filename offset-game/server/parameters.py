import ray


@ray.remote
class ParameterServer(object):
    def __init__(self):
        self.uav = []
        self.ugv = []
        self.grid_map = []
        self.targetpos = []
        self.primitive = []
        self.drone_num = []
        self.gui_param = {
            'target': self.targetpos,
            'primitive': self.primitive,
            'Drone_num': self.drone_num
        }
        self.actions_uav = {
            'uav_p_1': {
                'primitive': 'planning',
                'n_vehicles': 20,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'uav',
                'centroid_pos': [],
                'platoon_id': 1,
                'execute': True
            },
            'uav_p_2': {
                'primitive': 'planning',
                'n_vehicles': 0,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'uav',
                'centroid_pos': [],
                'platoon_id': 2,
                'execute': True
            },
            'uav_p_3': {
                'primitive': 'planning',
                'n_vehicles': 0,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'uav',
                'centroid_pos': [],
                'platoon_id': 3,
                'execute': True
            }
        }

        self.actions_ugv = {
            'ugv_p_1': {
                'primitive': 'planning',
                'n_vehicles': 12,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'ugv',
                'centroid_pos': [],
                'platoon_id': 1,
                'execute': True
            },
            'ugv_p_2': {
                'primitive': 'planning',
                'n_vehicles': 0,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'ugv',
                'centroid_pos': [],
                'platoon_id': 2,
                'execute': True
            },
            'ugv_p_3': {
                'primitive': 'planning',
                'n_vehicles': 0,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'ugv',
                'centroid_pos': [],
                'platoon_id': 3,
                'execute': True
            }
        }
        return None

    def get_actions(self):
        return self.actions_uav, self.actions_ugv

    def set_actions(self, actions):
        if actions['vehicles_type'] == 'uav':
            key = 'uav_p_' + str(actions['platoon_id'])
            self.actions_uav[key] = actions
        else:
            key = 'ugv_p_' + str(actions['platoon_id'])
            self.actions_ugv[key] = actions
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
