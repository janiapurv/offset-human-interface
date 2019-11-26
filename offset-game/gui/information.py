import pygame


def get_window_size(screen_size):
    size = []
    for i in range(6):
        temp = [0.19 * screen_size[0], 0.245 * screen_size[1]]
        size.append(temp)

    return size


def get_position(screen_size):
    position = []
    position.append([10 + 0.6 * screen_size[0], 7 + 0.0 * screen_size[1]])
    position.append([5 + 0.8 * screen_size[0], 7 + 0.0 * screen_size[1]])
    position.append([10 + 0.6 * screen_size[0], 7 + .25 * screen_size[1]])
    position.append([5 + 0.8 * screen_size[0], 7 + .25 * screen_size[1]])
    position.append([10 + 0.6 * screen_size[0], 7 + .5 * screen_size[1]])
    position.append([5 + 0.8 * screen_size[0], 7 + .5 * screen_size[1]])
    position.append([10 + 0.6 * screen_size[0], 10 + .75 * screen_size[1]])
    return position


class Information(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        super().__init__()
        self.size = (400, 500)
        self.position = get_position(screen_size)
        self.surf1 = get_window_size(screen_size)
        for i in range(6):
            self.surface = pygame.Surface((self.surf1[i][0], self.surf1[i][1]))
            screen.blit(self.surface, self.position[i])
            self.surface.fill((0, 0, 0))
