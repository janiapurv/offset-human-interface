# Extraction Layer
Primativelist = []
Dronenumberlist = []
targetpositionlist = []
Drone_posuav = []
Drone_posugv = []


class Extraction():
    def __init__(self):
        return None

    def Primative(action, ps):
        Primativelist.append(action)
        ps.set_actions(action)

    def targetpostion(x, y, ps):
        targetpositionlist.append([x, y])
