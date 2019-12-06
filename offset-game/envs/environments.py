import time
import math
from pathlib import Path

import numpy as np

import ray

from .base_env import BaseEnv
from .agents import UAV, UGV
from .state_manager import StateManager
from .states import State
from .actions import Action
from .action_manager import ActionManager
from .rewards import BenningReward


def update_parameter_server(ps, state={}, action={}):
    if state:
        ps.set_state(state)

    if action:
        ps.set_action(action)
    return None


@ray.remote
class Benning(BaseEnv):
    def __init__(self, config):
        # Inherit base env
        super().__init__(config)

        # Environment parameters
        self.current_time = config['simulation']['current_time']
        self.done = False
        self.config = config

        # Load the environment
        if self.config['simulation']['collision_free']:
            path = Path(
                __file__).parents[0] / 'urdf/environment_collision_free.urdf'
        else:
            path = Path(__file__).parents[0] / 'urdf/environment.urdf'
        self.p.loadURDF(str(path), [58.487, 23.655, 0.1],
                        self.p.getQuaternionFromEuler([0, 0, math.pi / 2]),
                        useFixedBase=True)

        # Setup the uav and ugv
        uav, ugv = self._initial_setup(UGV, UAV)

        # Initialize the state and action components
        self.state_manager = StateManager(uav, ugv, self.current_time,
                                          self.config)
        self.state = State(self.state_manager)
        self.reward = BenningReward(self.state_manager)
        self.action = Action(self.state_manager)
        self.action_manager = ActionManager(self.state_manager)

    def get_initial_position(self, agent, n_agents):
        grid = np.arange(n_agents).reshape(n_agents // 5, 5)
        pos_xy = np.where(grid == agent)
        return [pos_xy[0][0] * 20 + 10, pos_xy[1][0] * 20]

    def _initial_setup(self, UGV, UAV):
        # Number of UGV and UAV
        self.n_ugv = self.config['simulation']['n_ugv']
        self.n_uav = self.config['simulation']['n_uav']

        ugv, uav = [], []

        # Initialise the UGV and UAV
        init_orientation = self.p.getQuaternionFromEuler([math.pi / 2, 0, 0])
        for i, item in enumerate(range(self.n_ugv)):
            position = self.get_initial_position(item, self.n_ugv)
            init_pos = [position[0] * 0.25 + 2.5, position[1] * 0.25, 5]
            ugv.append(UGV(self.p, init_pos, init_orientation, i, self.config))

        for i, item in enumerate(range(self.n_uav)):
            position = self.get_initial_position(item, self.n_uav)
            init_pos = [position[0] * 0.25 + 2.5, position[1] * 0.25 - 1.5, 5]
            uav.append(UAV(self.p, init_pos, init_orientation, i, self.config))
        return uav, ugv

    def get_camera_image(self):
        """Get the camera image of the scene

        Returns
        -------
        tuple
            Three arrays corresponding to rgb, depth, and segmentation image.
        """
        upAxisIndex = 2
        camDistance = 500
        pixelWidth = 350
        pixelHeight = 700
        camTargetPos = [0, 80, 0]

        far = camDistance
        near = -far
        view_matrix = self.p.computeViewMatrixFromYawPitchRoll(
            camTargetPos, camDistance, 0, 90, 0, upAxisIndex)
        projection_matrix = self.p.computeProjectionMatrix(
            -90, 60, 150, -150, near, far)
        # Get depth values using the OpenGL renderer
        width, height, rgbImg, depthImg, segImg = self.p.getCameraImage(
            pixelWidth,
            pixelHeight,
            view_matrix,
            projection_matrix,
            renderer=self.p.ER_BULLET_HARDWARE_OPENGL)
        return rgbImg, depthImg, segImg

    def reset(self, ps):
        """
        Resets the position of all the robots
        """
        for vehicle in self.state_manager.uav:
            vehicle.reset()

        for vehicle in self.state_manager.ugv:
            vehicle.reset()

        for i in range(50):
            time.sleep(1 / 240)
            self.p.stepSimulation()

        # Update parameter server
        ps.update_states.remote(self.state_manager.uav, self.state_manager.ugv,
                                self.state_manager.grid_map)

        # call the state manager
        state = 0  # self.state.get_state()
        done = False
        return state, done

    def step(self, parameter_server):
        """Take a step in the environement
        """
        # Get the action from parameter server
        actions = ray.get(parameter_server.get_actions.remote())
        actions_uav, actions_ugv = actions['uav'], actions['ugv']

        # Execute the actions
        self.action_manager.primitive_execution(actions_uav, actions_ugv,
                                                self.p, parameter_server)
        return None

    def check_episode_done(self):
        done = False
        if self.current_time >= self.config['simulation']['total_time']:
            done = True
        if self.state_manager.found_goal:
            done = True
        return done

    def get_reward(self):
        """Update reward of all the agents
        """
        # Calculate the reward
        total_reward = self.reward.mission_reward(self.state_manager.ugv,
                                                  self.state_manager.uav,
                                                  self.config)
        for vehicle in self.state_manager.uav:
            vehicle.reward = total_reward

        for vehicle in self.state_manager.ugv:
            vehicle.reward = total_reward

        return total_reward
