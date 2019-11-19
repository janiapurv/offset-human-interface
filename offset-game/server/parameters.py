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
        self.state_param = {
            'uav': self.uav,
            'ugv': self.ugv,
            'map': self.grid_map
        }
        self.gui_param = {
            'target': self.targetpos,
            'primitive': self.primitive,
            'Drone_num': self.drone_num
        }
        return None

    def get_parameters(self, parameter_type):
        if parameter_type == 'state':
            param = self.state_param
        if parameter_type == 'gui':
            param = self.gui_param
        elif parameter_type == 'action':
            param = self.action_param
        return param

    def update_state_param(self, uav, ugv, grid_map):
        self.uav = uav
        self.ugv = ugv
        self.map = grid_map
        self.state_param = {
            'uav': self.uav,
            'ugv': self.ugv,
            'map': self.grid_map
        }
        return None

    def update_action_param(self, uav, ugv, grid_map):
        self.uav = uav
        self.ugv = ugv
        self.map = grid_map
        return None

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
