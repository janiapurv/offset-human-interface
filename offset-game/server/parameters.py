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
        return None

    def get_actions(self):
        self.actions_uav = {
            'uav_p_1': {
                'primitive': 'planning',
                'n_vehicles': 20,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'uav',
                'centroid_pos': [],
                'platoon_id': 1
            },
            'uav_p_2': {
                'primitive': 'planning',
                'n_vehicles': 10,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'uav',
                'centroid_pos': [],
                'platoon_id': 2
            },
            'uav_p_3': {
                'primitive': 'planning',
                'n_vehicles': 20,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'uav',
                'centroid_pos': [],
                'platoon_id': 3
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
                'platoon_id': 1
            },
            'ugv_p_2': {
                'primitive': 'planning',
                'n_vehicles': 9,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'ugv',
                'centroid_pos': [],
                'platoon_id': 2
            },
            'ugv_p_3': {
                'primitive': 'planning',
                'n_vehicles': 4,
                'target_pos': [20, 120],
                'vehicles_id': [],
                'vehicles_type': 'ugv',
                'centroid_pos': [],
                'platoon_id': 3
            }
        }
        return self.actions_uav, self.actions_ugv

    def set_actions(self, actions):
        if actions['vehicles_type'] == 'uav':
            key = 'uav_p_' + actions['platoon_id']
            self.actions_uav[key] = actions
        else:
            key = 'ugv_p_' + actions['platoon_id']
            self.actions_ugv = actions
        return None

    def set_states(self, uav, ugv, grid_map):
        self.uav = uav
        self.ugv = ugv
        self.map = grid_map
        self.states = {'uav': self.uav, 'ugv': self.ugv, 'map': self.grid_map}
        return None

    def get_states(self):
        return self.states

    def update_gui_param(self, targetpos, primitive, drone_num):
        self.targetpos = targetpos
        self.primitive = primitive
        self.drone_num = drone_num
        self.gui_param = {
            'target': self.targetpos,
            'primitive': self.primitive,
            'Drone_num': self.drone_num
        }
        return None
