import pygame

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
            pygame.draw.circle(temp, color, pos, 3)
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

    def check_map_pos(self, width, height):
        if self.map_pos[0] > 0:
            self.map_pos[0] = 0
        if self.map_pos[1] > 0:
            self.map_pos[1] = 0
        if abs(self.map_pos[0]) > width - self.screen_width + 600:
            self.map_pos[0] = -width + self.screen_width - 600
        if abs(self.map_pos[1]) > height - self.screen_height + 170:
            self.map_pos[1] = -height + self.screen_height - 170

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
        self.screen = screen
        self.screen.blit(self.surface, self.position)

        self.mouse_0 = MousePosition(0)
        self.mouse_2 = MousePosition(2)
        self.rect = []

        self.env_image = self.get_env_image()
        self.env_image = pygame.transform.scale(
            self.env_image, (screen_size[0], screen_size[1]))
        self.surface.blit(self.env_image, (0, 0))

        self.benning = Benning()
        self.allocate = TaskAllocation()
        self.pan_zoom = PanZoom(self.surface, self.screen_size, self.env_image)

        # Some color
        self.BLACK = (0, 0, 0)

    def get_env_image(self):
        # arr = imread('offset-game/gui/images/Benning.png')
        # array = ((arr - arr.min()) *
        #          (1 / (arr.max() - arr.min()) * 255)).astype('uint8')
        # array = np.swapaxes(array, 0, 1)
        # image = pygame.surfarray.make_surface(array[:, :, 0:3])
        image = pygame.image.load(
            'offset-game/gui/images/Benning.png').convert()
        return image

    def update(self, states, actions, ps):
        # Get states
        states_uav, states_ugv = states['uav'], states['ugv']
        env_updated = self.benning.update_drones(self.env_image, states_uav,
                                                 states_ugv)
        self.pan_zoom.pan(self.mouse_2.position(), env_updated)

        # Task allocation
        mouse_draw(self.mouse_0.position(), self.surface)

        mouse_button = pygame.mouse.get_pressed()
        pixel_centroids = []
        if mouse_button[0]:
            self.rect.append(mouse_draw(self.mouse_0.position(), self.surface))
        elif not mouse_button[0]:
            if self.rect:
                map_pos = self.pan_zoom.get_current_map_pos()
                temp = self.rect[-1]
                temp[0] = temp[0] - map_pos[0]
                temp[1] = temp[1] - map_pos[1]
                pixel_centroids = self.allocate.select_platoon(
                    states, actions, temp)
                self.rect = []
        # # Draw a circle around them platoons
        # for center in pixel_centroids:
        #     pygame.draw.circle(self.surface, self.BLACK, center, 20, 5)

        if mouse_button[1]:
            x, y = pygame.mouse.get_pos()
            map_pos = self.pan_zoom.get_current_map_pos()
            target_pos = [x - map_pos[0], y - map_pos[1]]
            self.allocate.assign_target(actions, target_pos, ps)
            pygame.draw.circle(self.surface, (0, 0, 0), [x, y], 5)

        # Pause the game
        key = pygame.key.get_pressed()
        if key[pygame.K_x]:
            actions_uav, actions_ugv = actions['uav'], actions['ugv']
            for key in actions_uav:
                actions_uav[key]['execute'] = False
            for key in actions_ugv:
                actions_ugv[key]['execute'] = False
            ps.update_actions.remote(actions_uav, actions_ugv)

        # Resume the game
        key = pygame.key.get_pressed()
        if key[pygame.K_c]:
            # Get actions
            actions_uav, actions_ugv = actions['uav'], actions['ugv']
            for key in actions_uav:
                actions_uav[key]['execute'] = True
                actions_uav[key]['initial_formation'] = True
            for key in actions_ugv:
                actions_ugv[key]['execute'] = True
                actions_ugv[key]['initial_formation'] = True
            ps.update_actions.remote(actions_uav, actions_ugv)

        self.screen.blit(self.surface, self.position)
