import time
import math
from pathlib import Path

import ray

from .base_env import BaseEnv
from .agents import UAV, UGV
from .state_manager import StateManager
from .states import State
from .actions import Action
from .action_manager import ActionManager
from .rewards import BenningReward


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
        uav, ugv = super()._initial_setup(UGV, UAV)

        # Initialize the state and action components
        self.state_manager = StateManager(uav, ugv, self.current_time,
                                          self.config)
        self.state = State(self.state_manager)
        self.reward = BenningReward(self.state_manager)
        self.action = Action(self.state_manager)
        self.action_manager = ActionManager(self.state_manager)

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
        ps.set_states.remote(self.state_manager.uav, self.state_manager.ugv,
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
        # # Update state manager for progress
        # self.state_manager.update_progress()

        # # Get the new encoded state
        new_state = 0  # self.state.get_state()

        # # Get reward
        reward = 0  # self.get_reward()

        # # Is episode done
        done = 0  # self.check_episode_done()

        return new_state, reward, done

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
