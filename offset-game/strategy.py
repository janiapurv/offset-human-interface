import pygame
from utils import Button


def get_window_size(screen_size):
    size = (0.75 * screen_size[0], 0.225 * screen_size[1])
    return size


def get_position(screen_size):
    position = (5 + 0 * screen_size[0], 10 + 0.75 * screen_size[1])
    return position


class Strategy(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        super().__init__()
        self.size = get_window_size(screen_size)
        self.position = get_position(screen_size)
        self.surface = pygame.Surface(get_window_size(screen_size))
        self.surface.fill((0, 0, 0))
        self.screen = screen
        self.screen.blit(self.surface, self.position)

    def path_planning(self, event):
        SIZE = min(self.surface.get_size())
        path = 'images/path_planning.png'
        icon_position = (5, 25)
        button = Button(self.surface, icon_position, (SIZE, SIZE), path)
        button.event_handler(self.position, icon_position, event)
        if button.pressed:
            # perform some action
            print('Path planning')

    def mapping(self, event):
        SIZE = min(self.surface.get_size())
        path = 'images/mapping.png'
        icon_position = (100, 25)
        button = Button(self.surface, icon_position, (SIZE, SIZE), path)
        button.event_handler(self.position, icon_position, event)
        if button.pressed:
            print('Mapping')

    def formation(self, event):
        SIZE = min(self.surface.get_size())
        path = 'images/formation.png'
        icon_position = (200, 25)
        button = Button(self.surface, icon_position, (SIZE, SIZE), path)
        button.event_handler(self.position, icon_position, event)
        if button.pressed:
            # Draw a rectangel undernead
            print('Formation')

    def target_search(self, event):
        SIZE = min(self.surface.get_size())
        path = 'images/target_search.png'
        icon_position = (300, 25)
        button = Button(self.surface, icon_position, (SIZE, SIZE), path)
        button.event_handler(self.position, icon_position, event)
        if button.pressed:
            print('Target search')

    def update(self, event):
        self.surface.fill((0, 0, 0))
        self.path_planning(event)
        self.mapping(event)
        self.formation(event)
        self.target_search(event)
        self.screen.blit(self.surface, self.position)
