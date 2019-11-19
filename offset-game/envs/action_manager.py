import math as mt
import numpy as np

from .primitive_manager import PrimitiveManager
from primitives.mrta.task_allocation import MRTA


class ActionManager(object):
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.config = state_manager.config
        self.mrta = MRTA()

        # Setup the platoons
        self._init_platoons_setup()
        return None

    def _init_platoons_setup(self):
        """Initial setup of platoons with primitive execution class
        """

        self.uav_platoon = []
        for i in range(self.config['simulation']['n_ugv_platoons']):
            self.uav_platoon.append(PrimitiveManager(self.state_manager))

        self.ugv_platoon = []
        for i in range(self.config['simulation']['n_ugv_platoons']):
            self.ugv_platoon.append(PrimitiveManager(self.state_manager))
        return None

    def get_robot_group_info(self, vehicles, decoded_actions):
        """Calculates the robot and group info needed for task allocation

        Parameters
        ----------
        vehicles : list
            A list of UAV or UGV vehicles class
        decoded_actions : array
            The decoded actions array

        Returns
        -------
        robotInfo, groupInfo, targetInfo
        """
        # Get the non idle vehicle info and update it
        robotInfo = np.zeros((len(vehicles), 3))
        for i, vehicle in enumerate(vehicles):
            robotInfo[i, 0:2] = vehicle.current_pos[0:2]
            if vehicle.type == 'uav':
                robotInfo[i, 2] = vehicle.battery
            else:
                robotInfo[i, 2] = vehicle.ammo

        # Get the group/target info
        groupInfo = np.zeros((len(decoded_actions), 6))
        for i, actions in enumerate(decoded_actions):
            info = self.state_manager.node_info(actions[2])
            groupInfo[i, 0:2] = info['position'][0:2]
            groupInfo[i, 2] = mt.floor(actions[0])
            groupInfo[i, 3] = groupInfo[i, 3] * 0 + 1
            groupInfo[i, 4] = groupInfo[i, 4] * 0
            groupInfo[i, 5] = groupInfo[i, 5] * 0 + 600
        return robotInfo, groupInfo

    def primitive_parameters(self, decode_actions, vehicles_id, type):
        info = {}
        info['vehicles_id'] = vehicles_id
        info['primitive_id'] = -1
        info['end_pos'] = [0, 0]
        info['formation_type'] = None
        info['vehicle_type'] = type

        # Decoded actions is of the form
        # ['n_vehicles', 'primitive_id', 'target_id']
        # should implement as a dict
        if decode_actions[1] == 1:
            target_info = self.state_manager.node_info(decode_actions[2])
            info['end_pos'] = target_info['position']
            info['primitive_id'] = decode_actions[1]

        elif decode_actions[1] == 2:
            target_info = self.state_manager.node_info(decode_actions[2])
            info['end_pos'] = target_info['position']
            if decode_actions[3] == 0:
                info['formation_type'] = 'solid'
            else:
                info['formation_type'] = 'ring'
            info['primitive_id'] = decode_actions[1]
        return info

    def perform_marta_task_allocation(self, decoded_actions_uav,
                                      decoded_actions_ugv):
        """Perfroms task allocation using MRTA

        Parameters
        ----------
        decoded_actions_uav : array
            UAV decoded actions
        decoded_actions_ugv : array
            UGV decoded actions
        """
        # UAV allocation
        robotInfo, groupInfo = self.get_robot_group_info(
            self.state_manager.uav, decoded_actions_uav)

        # MRTA
        robotInfo, groupCenter = self.mrta.allocateRobots(robotInfo, groupInfo)
        for i in range(self.config['simulation']['n_uav_platoons']):
            vehicles_id = [
                j for j, item in enumerate(robotInfo) if item - 1 == i
            ]
            parameters = self.primitive_parameters(decoded_actions_uav[i],
                                                   vehicles_id, 'uav')
            self.uav_platoon[i].set_parameters(parameters)

        # UGV allocation
        robotInfo, groupInfo = self.get_robot_group_info(
            self.state_manager.ugv, decoded_actions_uav)
        # MRTA
        robotInfo, groupCenter = self.mrta.allocateRobots(robotInfo, groupInfo)
        for i in range(self.config['simulation']['n_ugv_platoons']):
            vehicles_id = [
                j for j, item in enumerate(robotInfo) if item - 1 == i
            ]
            parameters = self.primitive_parameters(decoded_actions_ugv[i],
                                                   vehicles_id, 'ugv')
            self.ugv_platoon[i].set_parameters(parameters)
        return None

    def perform_task_allocation(self, decoded_actions_uav,
                                decoded_actions_ugv):
        """Perfroms task allocation using MRTA

        Parameters
        ----------
        decoded_actions_uav : array
            UAV decoded actions
        decoded_actions_ugv : array
            UGV decoded actions
        """
        ids = 0
        for i in range(self.config['simulation']['n_uav_platoons']):
            vehicles_id = list(range(ids, ids + decoded_actions_uav[i][0]))
            ids = ids + decoded_actions_uav[i][0]
            parameters = self.primitive_parameters(decoded_actions_uav[i],
                                                   vehicles_id, 'uav')
            self.uav_platoon[i].set_parameters(parameters)

        ids = 0
        for i in range(self.config['simulation']['n_ugv_platoons']):
            vehicles_id = list(range(ids, ids + decoded_actions_ugv[i][0]))
            ids = ids + decoded_actions_ugv[i][0]
            parameters = self.primitive_parameters(decoded_actions_ugv[i],
                                                   vehicles_id, 'ugv')
            self.ugv_platoon[i].set_parameters(parameters)
        return None

    def primitive_execution(self,
                            decoded_actions_uav,
                            decoded_actions_ugv,
                            p_simulation,
                            hand_coded=True):
        """Performs task execution

        Parameters
        ----------
        decoded_actions_uav : array
            UAV decoded actions
        decoded_actions_ugv : [type]
            UAV decoded actions
        p_simulation : bullet engine
            Bullet engine to execute the simulation
        hand_coded : bool
            Whether hand coded tactics are being used or not
        """

        if hand_coded:
            self.perform_task_allocation(decoded_actions_uav,
                                         decoded_actions_ugv)
        else:
            self.perform_marta_task_allocation(decoded_actions_uav,
                                               decoded_actions_ugv)

        done_rolling_primitive = False
        simulation_count = 0

        # Execute them
        for i in range(500):
            simulation_count += 1
            # Update the time
            done = []

            # Update all the uav vehicles
            for i in range(self.config['simulation']['n_uav_platoons']):
                if self.uav_platoon[i].n_vehicles > 0:
                    done.append(
                        self.uav_platoon[i].execute_primitive(p_simulation))

            # Update all the ugv vehicles
            for i in range(self.config['simulation']['n_ugv_platoons']):
                if self.ugv_platoon[i].n_vehicles > 0:
                    done.append(
                        self.ugv_platoon[i].execute_primitive(p_simulation))

            if all(item for item in done):
                done_rolling_primitive = True
                break
            # p_simulation.stepSimulation()

        simulation_time = simulation_count * self.config['simulation'][
            'time_step']
        self.state_manager.current_time += simulation_time
        return done_rolling_primitive
