import math
import pygame


class MousePosition:
    def __init__(self, key):
        self.pos = []
        self.key = key

    def position(self):
        if pygame.mouse.get_pressed()[self.key]:
            self.pos.append(pygame.mouse.get_pos())
        else:
            self.pos = []

        return self.pos


class Button(object):
    def __init__(self, surface, icon_position, size, image_path):
        # create 3 images
        image = pygame.image.load(image_path)
        self.icon = pygame.transform.scale(
            image, (int(size[0] * 0.5), int(size[1] * 0.5)))
        self.rect = self.icon.get_rect()
        self.surface = surface
        surface.blit(self.icon, icon_position)
        self.pressed = False

    def indication(self, surface, position, icon_position):
        x_pos = position[0] + icon_position[0]
        y_pos = position[1] + icon_position[1] + 50
        pygame.draw.rect(surface, (255, 255, 255), (x_pos, y_pos, 100, 100),
                         10)

    def event_handler(self, position, icon_position, event):
        self.pressed = False
        # change selected color if rectange clicked
        if event.type == pygame.MOUSEBUTTONDOWN:  # is some button clicked
            self.shifted_pos = (event.pos[0] - position[0] - icon_position[0],
                                event.pos[1] - position[1] - icon_position[1])
            if event.button == 1:  # is left button clicked
                if self.rect.collidepoint(self.shifted_pos):
                    self.pressed = True


def get_rectangle_param(intial_pos, final_pos):

    dist = math.sqrt((final_pos[0] - intial_pos[0])**2 +
                     (final_pos[1] - intial_pos[1])**2)
    angle = math.atan2((final_pos[1] - intial_pos[1]),
                       (final_pos[0] - intial_pos[0]))
    width = math.cos(angle) * dist
    height = math.sin(angle) * dist

    return width, height
