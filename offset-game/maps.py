import pygame
import numpy as np
from utils import (get_rectangle_param, MousePosition)


def mouse_draw(mouse_pos, surface):
    if mouse_pos:
        width, height = get_rectangle_param(mouse_pos[0], mouse_pos[-1])
        pygame.draw.rect(surface, (0, 0, 255),
                         (mouse_pos[0][0], mouse_pos[0][1], width, height), 5)


def get_window_size(screen_size):
    size = (int(0.75 * screen_size[0]), int(0.75 * screen_size[1]))
    return size


def get_position(screen_size):
    position = (5 + 0 * screen_size[0], 5 + 0 * screen_size[1])
    return position


class Map(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        super().__init__()
        self.screen_size = screen_size
        self.position = get_position(screen_size)
        self.size = get_window_size(screen_size)
        self.surface = pygame.Surface(self.size)
        self.surface.fill((0, 0, 0))
        self.screen = screen
        self.screen.blit(self.surface, self.position)
        self.mouse = MousePosition()

    def update(self, event):
        x, y = pygame.mouse.get_pos()
        self.surface.fill((0, 0, 0))
        if (x <= self.size[0]) and (y <= self.size[1]):
            mouse_draw(self.mouse.position(), self.surface)
            image_array = np.random.randint(self.size[0], size=(2, 1))
            pygame.draw.circle(self.surface, (0, 255, 0),
                               (image_array[0], image_array[1]), 10)
            self.screen.blit(self.surface, self.position)
