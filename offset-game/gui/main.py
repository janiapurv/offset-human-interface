import pygame

import ray

from .maps import Map
from .strategy import Strategy
from .information import Information
from .fullmap import FullMap

import time


@ray.remote
class MainGUI:
    def __init__(self, screen_size, ps):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size, pygame.DOUBLEBUF)
        self.screen.fill([255, 255, 255])
        self.map = Map(self.screen, screen_size)
        self.strategy = Strategy(self.screen, screen_size, ps)
        self.information = Information(self.screen, screen_size)
        self.fullmap = FullMap(self.screen, screen_size)

    def run(self, ps):
        clock = pygame.time.Clock()
        start_time = time.time()
        while (time.time() - start_time) < 100:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

            # Get latest states and actions
            states_id = ps.get_states.remote()
            actions_id = ps.get_actions.remote()

            states, actions = ray.get([states_id, actions_id])

            # Update all the modules
            self.map.update(event, states, actions, ps)
            self.strategy.update(event)
            self.fullmap.update()
            pygame.display.update()
            clock.tick(60)
