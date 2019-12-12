import math

import pybullet as p
import pybullet_data
from pybullet_utils import bullet_client


class BaseEnv(object):
    def __init__(self, config):
        self.config = config
        # Usage mode
        if config['simulation']['headless']:
            self.p = bullet_client.BulletClient(connection_mode=p.DIRECT)
        else:
            self.p = bullet_client.BulletClient(connection_mode=p.GUI)
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
        # self.p.setRealTimeSimulation(1)

        # Setup ground
        plane = self.p.loadURDF("plane.urdf", [0, 0, 0],
                                self.p.getQuaternionFromEuler(
                                    [0, 0, math.pi / 2]),
                                useFixedBase=True,
                                globalScaling=20)
        self.p.changeVisualShape(plane, -1)

        return None
