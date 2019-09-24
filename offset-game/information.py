import pygame


def get_window_size(screen_size):
    size = (0.225 * screen_size[0], 0.75 * screen_size[1])
    return size


def get_position(screen_size):
    position = (10 + 0.75 * screen_size[0], 5 + 0.0 * screen_size[1])
    return position


class Information(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        super().__init__()
        self.position = get_position(screen_size)
        self.surface = pygame.Surface(get_window_size(screen_size))
        self.surface.fill((0, 0, 0))
        screen.blit(self.surface, self.position)

    def update(self, screen):
        self.surface.fill(pygame.Color('dodgerblue'))
