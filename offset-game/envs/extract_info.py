import numpy as np


def action_parameters(vehicles, parameters):
    centroid = get_centroid(vehicles)
    parameters['centroid_pos'] = centroid
    return parameters


def get_centroid(vehicles):
    """Get the centroid of the vehicles
        """
    centroid = []
    for vehicle in vehicles:
        centroid.append(vehicle.current_pos)
    centroid = np.mean(np.asarray(centroid), axis=0)
    return centroid[0:2]  # only x and y
