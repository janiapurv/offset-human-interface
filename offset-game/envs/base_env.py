import math

import numpy as np

import pybullet as p
import pybullet_data
import pybullet_utils.bullet_client as bc


class BaseEnv(object):
    def __init__(self, config):
        self.config = config
        # Usage mode
        if config['simulation']['headless']:
            self.p = bc.BulletClient(connection_mode=p.DIRECT)
        else:
            self.p = bc.BulletClient(connection_mode=p.GUI)
            self.p.resetDebugVisualizerCamera(cameraDistance=150,
                                              cameraYaw=0,
                                              cameraPitch=-89.999,
                                              cameraTargetPosition=[0, 80, 0])
        # Set gravity
        self.p.setGravity(0, 0, -9.81)
        self.p.setAdditionalSearchPath(pybullet_data.getDataPath())  # optional

        # Set parameters for simulation
        self.p.setPhysicsEngineParameter(
            fixedTimeStep=config['simulation']['time_step'], numSubSteps=1)

        # Setup ground
        plane = self.p.loadURDF("plane.urdf", [0, 0, 0],
                                self.p.getQuaternionFromEuler(
                                    [0, 0, math.pi / 2]),
                                useFixedBase=True,
                                globalScaling=20)
        self.p.changeVisualShape(plane, -1)
        return None

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
            ugv.append(UGV(init_pos, init_orientation, i, self.config))

        for i, item in enumerate(range(self.n_uav)):
            position = self.get_initial_position(item, self.n_uav)
            init_pos = [position[0] * 0.25 + 2.5, position[1] * 0.25 - 1.5, 5]
            uav.append(UAV(init_pos, init_orientation, i, self.config))
        return uav, ugv
