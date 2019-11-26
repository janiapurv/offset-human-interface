import pygame

from .primitive_manager import PrimitiveManager


class ActionManager(object):
    def __init__(self, map_instance, config):
        self.map = map_instance
        self.config = config
        self.initial_setup()
        return None

    def initial_setup(self):
        self.vehicle_group = pygame.sprite.Group()

        for i in range(self.config['simulation']['n_uav_platoons']):
            self.vehicle_group.add(PrimitiveManager(self.map, i + 1, 'uav'))

        for i in range(self.config['simulation']['n_ugv_platoons']):
            self.vehicle_group.add(PrimitiveManager(self.map, i + 1, 'ugv'))
        return None

    def update(self, states):
        self.map.env_surface = self.map.init_env_surface.copy()
        # self.map.screen.blit(self.map.init_surface, self.map.position)
        self.vehicle_group.update(states)
        self.map.screen.blit(self.map.surface, self.map.position)
        return None
