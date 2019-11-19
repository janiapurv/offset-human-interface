import ray


@ray.remote
class ParameterServer(object):
    def __init__(self):
        self.uav = []
        self.ugv = []
        self.grid_map = []
        self.state_param = {
            'uav': self.uav,
            'ugv': self.ugv,
            'map': self.grid_map
        }
        return None

    def get_parameters(self, parameter_type):
        if parameter_type == 'state':
            param = self.state_param
        elif parameter_type == 'action':
            param = self.action_param
        return param

    def update(self):
        self.state_param = {
            'uav': self.uav,
            'ugv': self.ugv,
            'map': self.grid_map
        }

    def update_state_param(self, uav, ugv, grid_map):
        self.uav = uav
        self.ugv = ugv
        self.map = grid_map

        # Update parameters
        self.update()
        return None

    def update_action_param(self, uav, ugv, grid_map):
        self.uav = uav
        self.ugv = ugv
        self.map = grid_map
        return None
