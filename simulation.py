from graph import GraphModel
from drone import Drone


class Simulation:
    """
    Manages the simulation of drones moving through the graph.
    """
    def __init__(self, nb_drones: int, graph: GraphModel,
                 start: str, end: str) -> None:
        self.nb_drones = nb_drones
        self.graph = graph
        self.start = start
        self.end = end
        self.drones = [Drone(i + 1, start) for i in range(nb_drones)]

    def is_reachable(self) -> bool:
        """Check if the end hub is reachable from the start hub."""
        visited = set()
        queue = [self.start]
        while queue:
            zone = queue.pop(0)
            if zone == self.end:
                return True
            if zone not in visited:
                visited.add(zone)
            for n in self.graph.zones[zone].neighbors:
                if n not in visited:
                    queue.append(n)
        return False

    def run(self):
        if self.is_reachable():
            print("Running simulation...")
        else:
            print("End hub is not reachable from the start hub.")