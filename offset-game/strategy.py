import pygame


def get_window_size(screen_size):
    size = (0.75 * screen_size[0], 0.225 * screen_size[1])
    return size


def get_position(screen_size):
    position = (5 + 0 * screen_size[0], 10 + 0.75 * screen_size[1])
    return position


class Strategy(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        super().__init__()
        self.position = get_position(screen_size)
        self.surface = pygame.Surface(get_window_size(screen_size))
        self.surface.fill((0, 0, 0))
        self.screen = screen
        self.screen.blit(self.surface, self.position)
        # Add four buttons

    def path_planning(self):
        SIZE = min(self.surface.get_size())
        image = pygame.image.load('images/path_planning.png')
        image = pygame.transform.scale(image,
                                       (int(SIZE * 0.5), int(SIZE * 0.5)))
        self.surface.blit(image, (0, 0))

    def update(self):
        self.surface.fill((0, 0, 0))
        self.path_planning()
        self.screen.blit(self.surface, self.position)
