import pygame
from .utils import Button
# import gui.inputbox


def get_window_size(screen_size):
    size = (0.35 * screen_size[0], 0.225 * screen_size[1])
    return size


def get_position(screen_size):
    position = (5 + 0 * screen_size[0], 10 + 0.75 * screen_size[1])
    return position


class Strategy(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size, ps):
        super().__init__()
        self.size = get_window_size(screen_size)
        self.position = get_position(screen_size)
        self.surface = pygame.Surface(get_window_size(screen_size))
        self.surface.fill((0, 0, 0))
        self.screen = screen
        self.screen.blit(self.surface, self.position)
        self.ps = ps

    def path_planning(self, event):
        SIZE = min(self.surface.get_size())
        path = 'offset-game/gui/images/path_planning.png'
        icon_position = ((self.size[0] / 5) - 50, 35)
        button = Button(self.surface, icon_position, (SIZE, SIZE), path,
                        str('path_panning'))
        button.event_handler(self.position, icon_position, event)
        if button.pressed:
            action = str('path_planning')
            self.ex.Primative(action, self.ps)

    def mapping(self, event):
        SIZE = min(self.surface.get_size())
        path = 'offset-game/gui/images/mapping.png'
        icon_position = ((2 * self.size[0] / 5) - 50, 35)
        button = Button(self.surface, icon_position, (SIZE, SIZE), path,
                        str('mapping'))
        button.event_handler(self.position, icon_position, event)
        if button.pressed:
            action = str('mapping')
            self.ex.Primative(action, self.ps)
        # answer = gui.inputbox.ask(self.screen, "Number of Drones", self.ps)

    def formation(self, event):
        SIZE = min(self.surface.get_size())
        path = 'offset-game/gui/images/formation.png'
        icon_position = ((3 * self.size[0] / 5) - 50, 35)
        button = Button(self.surface, icon_position, (SIZE, SIZE), path,
                        str('formation'))
        button.event_handler(self.position, icon_position, event)
        if button.pressed:
            action = str('formation')
            self.ex.Primative(action, self.ps)
            button.indication(self.surface, self.position, icon_position)

    def target_search(self, event):
        SIZE = min(self.surface.get_size())
        path = 'offset-game/gui/images/target_search.png'
        icon_position = ((4 * self.size[0] / 5) - 50, 35)
        button = Button(self.surface, icon_position, (SIZE, SIZE), path,
                        str('target_search'))
        button.event_handler(self.position, icon_position, event)
        if button.pressed:
            action = str('target_search')
            self.ex.Primative(action, self.ps)

    def update(self, event):
        self.surface.fill((0, 0, 0))
        self.path_planning(event)
        self.mapping(event)
        self.formation(event)
        self.target_search(event)
        self.screen.blit(self.surface, self.position)
