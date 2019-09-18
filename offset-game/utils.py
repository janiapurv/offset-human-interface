import math
import pygame


class MousePosition:
    def __init__(self):
        self.pos = []

    def position(self):
        if pygame.mouse.get_pressed()[0]:
            self.pos.append(pygame.mouse.get_pos())
        else:
            self.pos = []

        return self.pos


def get_rectangle_param(intial_pos, final_pos):

    dist = math.sqrt((final_pos[0] - intial_pos[0])**2 +
                     (final_pos[1] - intial_pos[1])**2)
    angle = math.atan2((final_pos[1] - intial_pos[1]),
                       (final_pos[0] - intial_pos[0]))
    width = math.cos(angle) * dist
    height = math.sin(angle) * dist

    return width, height
