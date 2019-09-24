import pygame
from utils import (get_rectangle_param, MousePosition)


def mouse_draw(mouse_pos, surface, map_image):
    if mouse_pos:
        width, height = get_rectangle_param(mouse_pos[0], mouse_pos[-1])
        # surface.blit(map_image, (0, 0))
        pygame.draw.rect(surface, (0, 0, 255),
                         (mouse_pos[0][0], mouse_pos[0][1], width, height), 5)


def get_window_size(screen_size):
    size = (int(0.75 * screen_size[0]), int(0.75 * screen_size[1]))
    return size


def get_position(screen_size):
    position = (5 + 0 * screen_size[0], 5 + 0 * screen_size[1])
    return position


class PanZoom(pygame.sprite.Sprite):
    """For panning and zooming
    """
    def __init__(self, surface, map_image):
        self.surface = surface
        self.map_image = map_image
        self.map_pos = self.map_image.get_rect()
        self.mouse = MousePosition(0)

    def pan(self, map_image, mouse_pos):
        # intial_mouse = mouse_pos[0]
        # final_mouse = mouse_pos[-1]
        # dx_mouse = final_mouse[0] - intial_mouse[0]
        # dy_mouse = final_mouse[1] - intial_mouse[1]
        width, height = get_rectangle_param(mouse_pos[0], mouse_pos[-1])
        self.map_pos[0] = self.map_pos[0] + int(0.5 * width)
        self.map_pos[1] = self.map_pos[1] + int(0.5 * height)
        self.map_image = pygame.transform.scale(
            map_image, (self.map_pos.width, self.map_pos.height))
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.map_image, self.map_pos)

    def zoom(self, map_image, event):
        if event.button == 4:
            self.map_pos.width = self.map_pos.width + 100
            self.map_pos.height = self.map_pos.height + 100
        elif event.button == 5:
            self.map_pos.width = self.map_pos.width - 100
            self.map_pos.height = self.map_pos.height - 100
        self.map_image = pygame.transform.scale(
            map_image, (self.map_pos.width, self.map_pos.height))
        self.surface.blit(self.map_image, (0, 0))

    def draw_updated_map(self):
        self.surface.blit(self.map_image, self.map_pos)


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
        self.mouse = MousePosition(0)
        self.map_image = pygame.image.load("images/map.png")
        self.pan_zoom = PanZoom(self.surface, self.map_image)

    def draw_image(self):
        scale_x = self.surface.get_rect().width
        scale_y = self.surface.get_rect().height
        self.map_image = pygame.transform.scale(self.map_image,
                                                (scale_x, scale_y))
        self.surface.blit(self.map_image, (0, 0))
        self.screen.blit(self.surface, self.position)

    def update(self, event):
        x, y = pygame.mouse.get_pos()
        # self.surface.blit(self.map_image, (0, 0))
        keys = pygame.key.get_pressed()
        if (x <= self.size[0]) and (y <= self.size[1]):
            if self.mouse.position() and not keys[pygame.K_s]:
                self.pan_zoom.pan(self.map_image, self.mouse.position())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.pan_zoom.zoom(self.map_image, event)
            else:
                self.pan_zoom.draw_updated_map()
            if keys[pygame.K_s]:
                mouse_draw(self.mouse.position(), self.surface, self.map_image)
            if pygame.mouse.get_pressed()[2]:
                self.map_image = pygame.image.load("images/map.png")
                self.pan_zoom = PanZoom(self.surface, self.map_image)
                self.surface.blit(self.map_image, (0, 0))

            self.screen.blit(self.surface, self.position)
