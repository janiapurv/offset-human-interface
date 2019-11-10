import ray
import time

import pybullet as p

from .state_manager import StateManager
from .states import State
from .actions import Action
from .action_manager import ActionManager
from .rewards import BenningReward


@ray.remote
class Benning():
    def __init__(self, config):
        if config['simulation']['headless']:
            p.connect(p.DIRECT)  # Non-graphical version
        else:
            p.connect(p.GUI)
            p.resetDebugVisualizerCamera(cameraDistance=150,
                                         cameraYaw=0,
                                         cameraPitch=-89.999,
                                         cameraTargetPosition=[0, 80, 0])
        # Environment parameters
        self.current_time = config['simulation']['current_time']
        self.done = False
        self.config = config

        # Parameters for simulation
        p.setGravity(0, 0, -9.81)
        p.setRealTimeSimulation(1)

        # Initialize the state and action components
        self.state_manager = StateManager(self.current_time, self.config)
        self.state_manager._initial_mission_setup()
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
        view_matrix = p.computeViewMatrixFromYawPitchRoll(
            camTargetPos, camDistance, 0, 90, 0, upAxisIndex)
        projection_matrix = p.computeProjectionMatrix(-90, 60, 150, -150, near,
                                                      far)
        # Get depth values using the OpenGL renderer
        width, height, rgbImg, depthImg, segImg = p.getCameraImage(
            pixelWidth,
            pixelHeight,
            view_matrix,
            projection_matrix,
            renderer=p.ER_BULLET_HARDWARE_OPENGL)
        return rgbImg, depthImg, segImg

    def reset(self, ps):
        """
        Resets the position of all the robots
        """
        for vehicle in self.state_manager.uav:
            vehicle.reset()

        for vehicle in self.state_manager.ugv:
            vehicle.reset()

        for i in range(200):
            time.sleep(1 / 240)
            p.stepSimulation()

        # Update parameter server
        ps.update_state_param.remote(self.state_manager.uav,
                                     self.state_manager.uav,
                                     self.state_manager.grid_map)

        # call the state manager
        state = 0  # self.state.get_state()
        done = False
        return state, done

    def step(self, parameter_server, action):
        """Take a step in the environement
        """

        # Get the action from parameter server

        # Action splitting
        decoded_actions_uav = action[0:3]
        decoded_actions_ugv = action[3:]

        # Execute the actions
        done = self.action_manager.primitive_execution(decoded_actions_uav,
                                                       decoded_actions_ugv, p,
                                                       parameter_server)
        # Update state manager for progress
        self.state_manager.update_progress()
        # Get the new encoded state
        new_state = self.state.get_state()
        # Get reward
        reward = self.get_reward()
        # Is episode done
        done = self.check_episode_done()

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
