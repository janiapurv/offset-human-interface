import pygame
from maps import Map
from strategy import Strategy
from information import Information
from fullmap import FullMap

pygame.init()


class Main:
    def __init__(self, screen_size):
        self.screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
        self.screen.fill([255, 255, 255])
        self.map = Map(self.screen, screen_size)
        self.strategy = Strategy(self.screen, screen_size)
        self.information = Information(self.screen, screen_size)
        self.fullmap = FullMap(self.screen, screen_size)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                # Update all the modules
                self.map.update(event)
                self.strategy.update()
                self.fullmap.update()
                pygame.display.update()
                clock.tick(60)


if __name__ == "__main__":
    game = Main((750, 750))
    game.run()
