import numpy as np

from scipy import interpolate

from primitives.planning.planners import SkeletonPlanning
from primitives.formation.control import FormationControl


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
        self.planning = SkeletonPlanning(self.state_manager.config,
                                         self.state_manager.grid_map)
        self.formation = FormationControl()
        return None

    def set_parameters(self, primitive_info):
        """Set up the parameters of the premitive execution

        Parameters
        ----------
        primitive_info: dict
            A dictionary containing information about vehicles
            and primitive realted parameters.
        """
        # Update vehicles
        self.vehicles_id = primitive_info['vehicles_id']

        if primitive_info['vehicle_type'] == 'uav':
            self.vehicles = [
                self.state_manager.uav[j] for j in self.vehicles_id
            ]
        else:
            self.vehicles = [
                self.state_manager.ugv[j] for j in self.vehicles_id
            ]
        self.n_vehicles = len(self.vehicles)

        # Primitive parameters
        self.primitive_id = primitive_info['primitive_id']
        self.formation_type = primitive_info['formation_type']
        self.end_pos = primitive_info['end_pos']
        self.count = 0

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
        self.start_pos = self.centroid_pos
        pixel_start = self.convert_pixel_ordinate(self.start_pos,
                                                  ispixel=False)
        pixel_end = self.convert_pixel_ordinate(self.end_pos, ispixel=False)
        path = self.planning.find_path(pixel_start, pixel_end, spline=False)

        # Convert to cartesian co-ordinates
        points = np.zeros((len(path), 2))
        for i, point in enumerate(path):
            points[i, :] = self.convert_pixel_ordinate(point, ispixel=True)

        # Depending on the distance select number of points of the path
        segment_length = np.linalg.norm(self.start_pos - self.end_pos)
        n_steps = np.floor(segment_length / 200 * 250)

        if points.shape[0] > 3:
            tck, u = interpolate.splprep(points.T)
            unew = np.linspace(u.min(), u.max(), n_steps)
            x_new, y_new = interpolate.splev(unew, tck)
            # points = interpcurve(250, x_new, y_new)
            # x_new, y_new = points[:, 0], points[:, 1]
        else:
            # Find unique points
            points = np.array(list(set(tuple(p) for p in points)))
            f = interpolate.interp1d(points[:, 0], points[:, 1])
            x_new = np.linspace(points[0, 0], points[-1, 0], 10)
            y_new = f(x_new)

        new_points = np.array([x_new, y_new]).T
        return new_points, points

    def execute_primitive(self, p_simulation):
        """Perform primitive execution
        """
        primitives = [self.planning_primitive, self.formation_primitive]
        done = primitives[self.primitive_id - 1]()

        # Step the simulation
        p_simulation.stepSimulation()
        return done

    def planning_primitive(self):
        """Performs path planning primitive
        """
        # Make vehicles non idle
        self.make_vehicles_nonidle()
        done_rolling = False

        if self.count == 0:
            # First point of formation
            self.centroid_pos = self.get_centroid()
            self.next_pos = self.centroid_pos
            done = self.formation_primitive()
            if done:
                self.count = 1
                self.new_points, points = self.get_spline_points()
        else:
            self.centroid_pos = self.get_centroid()
            distance = np.linalg.norm(self.centroid_pos - self.end_pos)

            if len(self.new_points) > 2 and distance > 5:
                self.next_pos = self.new_points[0]
                self.new_points = np.delete(self.new_points, 0, 0)
            else:
                self.next_pos = self.end_pos
            self.formation_primitive()

            if distance < 0.5:
                done_rolling = True

        if done_rolling:
            self.make_vehicles_idle()

        return done_rolling

    def formation_primitive(self):
        """Performs formation primitive
        """
        if self.primitive_id == 2:
            self.centroid_pos = self.end_pos
            self.next_pos = self.end_pos

        dt = self.config['simulation']['time_step']
        self.vehicles, done = self.formation.execute(self.vehicles,
                                                     self.next_pos,
                                                     self.centroid_pos, dt,
                                                     self.formation_type)
        for vehicle in self.vehicles:
            vehicle.set_position(vehicle.updated_pos)
        return done
