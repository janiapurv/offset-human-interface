import numpy as np
import ray

from primitives.planning.planners import SkeletonPlanning
from primitives.formation.control import FormationControl


def update_parameter_server(ps, state={}, action={}):
    if state:
        ps.set_state.remote(state, complexity=True)

    if action:
        ps.set_action.remote(action, complexity=True)
    return None


class PrimitiveManager(object):
    def __init__(self, state_manager):
        """A base class to perform different primitives.

        Parameters
        ----------
        state_manager : instance
            An instance of state manager
        """
        self.config = state_manager.config
        self.state_manager = state_manager

        # Instance of primitives
        self.planning = SkeletonPlanning(self.state_manager.config,
                                         self.state_manager.grid_map)
        self.formation = FormationControl()
        return None

    def set_action(self, action):
        """Set up the parameters of the premitive execution

        Parameters
        ----------
        primitive_parameters : dict
            A dictionary containing information about vehicles
            and primitive realted parameters.
        """
        # Primitive parameters
        self.action = action  # make a copy and use it everywhere
        self.state = action  # we have the same template for states also
        self.key = self.action['vehicles_type'] + '_p_' + str(
            self.action['platoon_id'])

        if self.action['vehicles_type'] == 'uav':
            self.vehicles = [
                self.state_manager.uav[j] for j in self.action['vehicles_id']
            ]
        else:
            self.vehicles = [
                self.state_manager.ugv[j] for j in self.action['vehicles_id']
            ]
        return None

    def make_vehicles_idle(self):
        """Make the vehicles idle
        """
        for vehicle in self.vehicles:
            vehicle.idle = True
        return None

    def make_vehicles_nonidle(self):
        """Make the vehicles non-idle
        """
        for vehicle in self.vehicles:
            vehicle.idle = False
        return None

    def get_centroid(self):
        """Get the centroid of the vehicles
        """
        centroid = []
        for vehicle in self.vehicles:
            centroid.append(vehicle.current_pos)
        centroid = np.mean(np.asarray(centroid), axis=0)
        return centroid[0:2]  # only x and y

    def convert_pixel_ordinate(self, point, ispixel):
        """Convert the given point from pixel to cartesian co-ordinate or vice-versa.

        Parameters
        ----------
        point : list
            A list containing x and y position in pixel or cartesian space.
        ispixel : bool
            If True, the given input 'point' is in pixel space
            else it is in cartesian space.

        Returns
        -------
        list
            A converted point to pixel or cartesian space
        """
        if not ispixel:
            converted = [point[0] / 0.42871 + 145, point[1] / 0.42871 + 115]
        else:
            converted = [(point[0] - 145) * 0.42871,
                         (point[1] - 115) * 0.42871]
        return converted

    def get_spline_points(self):
        """Get the spline fit of path from start to end

        Returns
        -------
        list
            A list of points which are the fitted spline.
        """
        # Perform planning and fit a spline
        self.action['start_pos'] = self.action['centroid_pos']
        pixel_start = self.convert_pixel_ordinate(self.action['start_pos'],
                                                  ispixel=False)
        pixel_end = self.convert_pixel_ordinate(self.action['target_pos'],
                                                ispixel=False)
        path = self.planning.find_path(pixel_start, pixel_end, spline=False)

        # Convert to cartesian co-ordinates
        points = np.zeros((len(path), 2))
        for i, point in enumerate(path):
            points[i, :] = self.convert_pixel_ordinate(point, ispixel=True)

        # As of now don't fit any splines
        x_new, y_new = points[:, 0], points[:, 1]
        new_points = np.array([x_new, y_new]).T
        return new_points, points

    def execute_primitive(self, pb, ps):
        """Perform primitive execution
        """
        primitives = {
            'planning': self.planning_primitive,
            'formation': self.formation_primitive
        }

        # Get the latest actions
        actions = ray.get(ps.get_actions.remote(complexity=True))
        self.action = actions[self.action['vehicles_type']][self.key]

        if self.action['execute'] and self.action['n_vehicles'] > 0:
            # Start executing the primitive
            done = primitives[self.action['primitive']](ps)

            # Step the simulation
            pb.stepSimulation()

            # Set the actions and states
            self.action['centroid_pos'] = self.get_centroid()
            # Since we are using same template for states and actions
            self.state['vehicles'] = self.vehicles
            self.state['centroid_pos'] = self.action['centroid_pos']

            # Update parameter server
            update_parameter_server(ps, state=self.state, action=self.action)
        else:
            done = False
        return done

    def planning_primitive(self, ps):
        """Performs path planning primitive
        """
        # Make vehicles non idle
        done_rolling = False
        self.make_vehicles_nonidle()

        # Initial formation
        if self.action['initial_formation']:
            # First point of formation
            self.action['centroid_pos'] = self.get_centroid()
            self.action['next_pos'] = self.action['centroid_pos']
            done = self.formation_primitive(ps)
            if done:
                self.action['initial_formation'] = False
                self.new_points, points = self.get_spline_points()

                # Update parameter server
                update_parameter_server(ps, action=self.action)
        else:
            self.action['centroid_pos'] = self.get_centroid()
            distance = np.linalg.norm(self.action['centroid_pos'] -
                                      self.action['target_pos'])
            if len(self.new_points) > 2 and distance > 2:
                self.action['next_pos'] = self.new_points[0]
                self.new_points = np.delete(self.new_points, 0, 0)
            else:
                self.action['next_pos'] = self.action['target_pos']
            self.formation_primitive(ps)

            if distance < 1:
                done_rolling = True

        if done_rolling:
            self.make_vehicles_idle()
        return done_rolling

    def formation_primitive(self, ps):
        """Performs formation primitive
        """
        if self.action['primitive'] == 'formation':
            self.action['centroid_pos'] = self.get_centroid()
            self.action['next_pos'] = self.action['target_pos']

        self.formation_type = 'solid'  # a place holder
        dt = self.config['simulation']['time_step']
        self.vehicles, done = self.formation.execute(
            self.vehicles, self.action['next_pos'],
            self.action['centroid_pos'], dt, self.formation_type)
        for vehicle in self.vehicles:
            vehicle.set_position(vehicle.updated_pos)
        return done
