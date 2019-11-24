import time

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
        """Initial setup of platoons with primitive execution class.
            Each platoon name is given as uxv_p_* where * is the platoon number
            and x is either 'a' or 'g' depending on platoon type.
            The containers used for platoons are dict where key is uxv_p_*

            As an example one of the keys is 'uav_p_1'
            which is platoon 1 of type uav

        """
        self.uav_platoons = {}
        for i in range(self.config['simulation']['n_uav_platoons']):
            key = 'uav_p_' + str(i + 1)
            self.uav_platoons[key] = PrimitiveManager(self.state_manager)

        self.ugv_platoons = {}
        for i in range(self.config['simulation']['n_ugv_platoons']):
            key = 'ugv_p_' + str(i + 1)
            self.ugv_platoons[key] = PrimitiveManager(self.state_manager)
        return None

    def perform_task_allocation(self, decoded_actions_uav,
                                decoded_actions_ugv):
        """Perfroms task allocation

        Parameters
        ----------
        decoded_actions_uav : array
            UAV decoded actions
        decoded_actions_ugv : array
            UGV decoded actions
        """
        ids = 0
        for key in self.uav_platoons:
            n_vehicles = decoded_actions_uav[key]['n_vehicles']
            # Execute only when there are more than 0 vehicles
            if n_vehicles < 1:
                decoded_actions_uav[key]['execute'] = False

            vehicles_id = list(range(ids, ids + n_vehicles))
            ids = ids + n_vehicles
            decoded_actions_uav[key]['vehicles_id'] = vehicles_id
            self.uav_platoons[key].set_action(decoded_actions_uav[key])

        ids = 0
        for key in self.ugv_platoons:
            n_vehicles = decoded_actions_ugv[key]['n_vehicles']
            # Execute only when there are more than 0 vehicles
            if n_vehicles < 1:
                decoded_actions_ugv[key]['execute'] = False

            # Set number of vehicles
            vehicles_id = list(range(ids, ids + n_vehicles))
            ids = ids + n_vehicles
            decoded_actions_ugv[key]['vehicles_id'] = vehicles_id
            self.ugv_platoons[key].set_action(decoded_actions_ugv[key])
        return None

    def primitive_execution(self,
                            decoded_actions_uav,
                            decoded_actions_ugv,
                            pb,
                            ps,
                            hand_coded=True):
        """Performs task execution

        Parameters
        ----------
        decoded_actions_uav : array
            UAV decoded actions
        decoded_actions_ugv : array
            UAV decoded actions
        pb : bullet engine
            Bullet engine to execute the simulation
        ps : parameter server instance
            An instance of parameter server to updated different parameters
        hand_coded : bool
            Whether hand coded tactics are being used or not
        """

        self.perform_task_allocation(decoded_actions_uav, decoded_actions_ugv)

        # Roll the primitives
        done_rolling_primitives = False
        simulation_count = 0
        start_time = time.time()
        current_time = 0
        duration = self.config['experiment']['duration']

        while not done_rolling_primitives and current_time <= duration:
            # Count number of steps
            simulation_count += 1

            primitives_done = []
            # Update all the uav vehicles and write to parameter server
            for key in self.uav_platoons:
                primitives_done.append(
                    self.uav_platoons[key].execute_primitive(pb, ps))

            # Update all the ugv vehicles and write to parameter server
            for key in self.ugv_platoons:
                primitives_done.append(
                    self.ugv_platoons[key].execute_primitive(pb, ps))

            if all(item for item in primitives_done):
                done_rolling_primitives = True
                break

            current_time = time.time() - start_time

        # Update the time
        simulation_time = simulation_count * self.config['simulation'][
            'time_step']
        self.state_manager.current_time += simulation_time

        return done_rolling_primitives
