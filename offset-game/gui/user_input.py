import pygame


class UserInput():
    def __init__(self):
        return None

    def update(self, actions, ps):
        # Pause the game
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
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
