import pygame
import pygame.gfxdraw

from .gif import GIFImage
from .task_allocation import TaskAllocation
from .utils import (get_rectangle_param, MousePosition)


def mouse_draw(mouse_pos, surface):
    if mouse_pos:
        width, height = get_rectangle_param(mouse_pos[0], mouse_pos[-1])
        pygame.draw.rect(surface, (0, 0, 255),
                         (mouse_pos[0][0], mouse_pos[0][1], width, height), 2)
        mouse_parameters = [mouse_pos[-1][0], mouse_pos[-1][1], width, height]
    else:
        mouse_parameters = []

    return mouse_parameters


def get_window_size(screen_size):
    size = (int(0.6 * screen_size[0]), int(0.75 * screen_size[1]))
    return size


def get_position(screen_size):
    position = (5 + 0 * screen_size[0], 5 + 0 * screen_size[1])
    return position


class Benning(pygame.sprite.Sprite):
    """Benning environment class
    """
    def __init__(self):
        return None

    def update_drones(self, surface, uav, ugv):
        temp = surface.copy()
        color, color2 = (0, 153, 76), (0, 0, 255)
        for vehicle in uav:
            pos = [
                int(vehicle.current_pos[1] / .2 + 420),
                int(vehicle.current_pos[0] / .2 + 340)
            ]
            # pygame.draw.circle(temp, color, pos, 3)
            pygame.gfxdraw.filled_circle(temp, pos[0], pos[1], 3, color)
            pygame.gfxdraw.aacircle(temp, pos[0], pos[1], 3, color)
        for vehicle in ugv:
            pos = [(vehicle.current_pos[1] / .2 + 420),
                   vehicle.current_pos[0] / .2 + 340]
            pygame.draw.rect(temp, color2, pygame.Rect(pos, [5, 5]))
        return temp


class PanZoom(pygame.sprite.Sprite):
    """For panning and zooming
    """
    def __init__(self, surface, screen_size, env_surface):
        self.surface = surface
        self.map_pos = env_surface.get_rect()

        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]
        return None

    def check_map_pos(self, width, height):
        if self.map_pos[0] > 0:
            self.map_pos[0] = 0
        if self.map_pos[1] > 0:
            self.map_pos[1] = 0
        if abs(self.map_pos[0]) > width - self.screen_width + 600:
            self.map_pos[0] = -width + self.screen_width - 600
        if abs(self.map_pos[1]) > height - self.screen_height + 170:
            self.map_pos[1] = -height + self.screen_height - 170
        return None

    def get_current_map_pos(self):
        return [self.map_pos[0], self.map_pos[1]]

    def pan(self, mouse_pos, env_surface):
        # Calculate the width and height
        width = env_surface.get_rect().width
        height = env_surface.get_rect().height

        if len(mouse_pos) > 1:
            intial_mouse = mouse_pos[-2]
            final_mouse = mouse_pos[-1]
            dx_mouse = final_mouse[0] - intial_mouse[0]
            dy_mouse = final_mouse[1] - intial_mouse[1]
        else:
            dx_mouse = 0
            dy_mouse = 0

        # Update the map pose
        self.map_pos[0] = dx_mouse + self.map_pos[0]
        self.map_pos[1] = dy_mouse + self.map_pos[1]

        # Check is the map of out of boundary
        self.check_map_pos(width, height)

        self.surface.blit(env_surface, self.map_pos)
        return None


class Map(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        self.screen_size = screen_size
        self.position = get_position(screen_size)
        self.size = get_window_size(screen_size)

        self.surface = pygame.Surface(self.size)
        self.screen = screen  # overall screen
        self.screen.blit(self.surface, self.position)

        self.mouse_0 = MousePosition(0)
        self.mouse_2 = MousePosition(2)
        self.rect = []

        self.env_image = self.get_env_image()
        self.env_image = pygame.transform.scale(
            self.env_image, (screen_size[0], screen_size[1]))
        self.surface.blit(self.env_image, (0, 0))

        # Components of map
        self.benning = Benning()
        self.smoke = GIFImage('offset-game/gui/images/smoke.gif',
                              transparency=True)
        self.allocate = TaskAllocation()
        self.pan_zoom = PanZoom(self.surface, self.screen_size, self.env_image)

        return None

    def get_env_image(self):
        image_path = 'offset-game/gui/images/Benning.png'
        image = pygame.image.load(image_path).convert()
        return image

    def update(self, states, actions, game_state, ps):
        # Get states
        states_uav, states_ugv = states['uav'], states['ugv']
        env_updated = self.benning.update_drones(self.env_image, states_uav,
                                                 states_ugv)
        self.pan_zoom.pan(self.mouse_2.position(), env_updated)

        # Task allocation
        mouse_draw(self.mouse_0.position(), self.surface)

        # Current map poisition
        map_pos = self.pan_zoom.get_current_map_pos()

        # Selection of platoons
        mouse_button = pygame.mouse.get_pressed()
        if mouse_button[0]:
            self.rect.append(mouse_draw(self.mouse_0.position(), self.surface))
        elif not mouse_button[0]:
            if self.rect:
                temp = self.rect[-1]
                temp[0] = temp[0] - map_pos[0]
                temp[1] = temp[1] - map_pos[1]
                self.allocate.select_platoon(states, actions, temp)
                self.rect = []

        # Providing the target position
        if mouse_button[1]:
            x, y = pygame.mouse.get_pos()
            target_pos = [x - map_pos[0], y - map_pos[1]]
            self.allocate.assign_target(actions, target_pos, ps)
            pygame.draw.circle(self.surface, (0, 0, 0), [x, y], 5)

        # Draw smoke
        self.smoke.render(self.surface, [400 + map_pos[0], 100 + map_pos[1]])

        # Pause and resume game
        if game_state['pause']:
            pygame.gfxdraw.filled_circle(self.surface, 25, 25, 15,
                                         (255, 255, 255))
            pygame.gfxdraw.aacircle(self.surface, 25, 25, 15, (255, 255, 255))

        # Blit the final surface to screen
        self.screen.blit(self.surface, self.position)
