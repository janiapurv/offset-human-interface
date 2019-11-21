import pygame


def get_window_size(screen_size):
    size = (.247 * screen_size[0], 0.225 * screen_size[1])
    return size


def get_position(screen_size):
    position = (-5 + .6 * screen_size[0] - .24 * screen_size[0],
                10 + 0.75 * screen_size[1])
    return position


class FullMap(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        super().__init__()
        self.map_image = pygame.image.load('offset-game/gui/Map/Benning.png')
        self.position = get_position(screen_size)
        self.surface = pygame.Surface(get_window_size(screen_size))
        self.surface.fill(pygame.Color('dodgerblue'))
        self.screen = screen
        self.screen.blit(self.surface, self.position)

    def update(self):
        scale_x = self.surface.get_rect().width
        scale_y = self.surface.get_rect().height
        self.map_image = pygame.transform.scale(self.map_image,
                                                (scale_x, scale_y))
        self.surface.blit(self.map_image, (0, 0))
        self.screen.blit(self.surface, self.position)
