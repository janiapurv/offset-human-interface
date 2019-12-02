import pygame
import numpy as np

from .primitive_manager import PrimitiveManager
from .primitive_manager import ComplexPrimitiveManager


class ActionManager(object):
    def __init__(self, map_instance, config):
        self.map = map_instance
        self.config = config
        self.initial_setup()
        self.initial_complexity_setup()
        return None

    def initial_setup(self):
        self.vehicle_group = pygame.sprite.Group()
        for i in range(self.config['simulation']['n_uav_platoons']):
            self.vehicle_group.add(PrimitiveManager(self.map, i + 1, 'uav'))

        for i in range(self.config['simulation']['n_ugv_platoons']):
            self.vehicle_group.add(PrimitiveManager(self.map, i + 1, 'ugv'))
        return None

    def initial_complexity_setup(self):
        self.vehicle_red_group = pygame.sprite.Group()
        for i in range(self.config['simulation']['n_uav_platoons']):
            self.vehicle_red_group.add(
                ComplexPrimitiveManager(self.map, i + 1, 'uav'))

        for i in range(self.config['simulation']['n_ugv_platoons']):
            self.vehicle_red_group.add(
                ComplexPrimitiveManager(self.map, i + 1, 'ugv'))
        return None

    def update(self, states, complexity_states):
        self.map.env_surface = self.map.init_env_surface.copy()
        self.vehicle_group.update(states)
        self.vehicle_red_group.update(complexity_states)
        self.map.screen.blit(self.map.surface, self.map.position)
        return None

    def convert_to_pixel(self, points):
        pos = [int(points[1] / .2 + 420), int(points[0] / .2 + 340)]
        return np.asarray(pos)

    def check_perimeter(self, states, complexity_states, ps):
        state_uav, state_ugv = states['uav'], states['ugv']
        complex_state_uav, complex_state_ugv = complexity_states[
            'uav'], complexity_states['ugv']
        centroid = {}
        complex_centroid = {}
        for key in state_uav:
            centroid[key] = state_uav[key]['centroid_pos']
            complex_centroid[key] = complex_state_uav[key]['centroid_pos']
        for key in state_ugv:
            centroid[key] = state_ugv[key]['centroid_pos']
            complex_centroid[key] = complex_state_ugv[key]['centroid_pos']

        # Calculate the distance
        cent_pos = np.array(list(centroid.values()))
        complex_pos = np.array(list(complex_centroid.values()))
        dist = np.linalg.norm(cent_pos - complex_pos, axis=1)
        mask = dist < self.config['experiment']['perimeter_distance']
        for i, item in enumerate(mask[0:3]):
            if item:
                platoon = 'uav_p_' + str(i + 1)
                complexity_states['uav'][platoon]['with_in_perimeter'] = True
                ps.set_complexity_states.remote(
                    complexity_states['uav'][platoon])
