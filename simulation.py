from graph import GraphModel
from drone import Drone

COLOR_MAP = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "black": "\033[30m",
    "purple": "\033[35m",
    "brown": "\033[33m",
    "orange": "\033[38;5;208m",
    "maroon": "\033[38;5;88m",
    "gold": "\033[38;5;220m",
    "darkred": "\033[38;5;52m",
    "violet": "\033[38;5;177m",
    "crimson": "\033[38;5;160m",
    "rainbow": "\033[38;5;214m",
}
RESET = "\033[0m"


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

    def colorize_zone(self, zone_name):
        color = self.graph.zones[zone_name].color
        if color and color.lower() in COLOR_MAP:
            return f"{COLOR_MAP[color.lower()]}{zone_name}{RESET}"
        return zone_name

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

    def find_path(self, start: str, end: str) -> list[str]:
        """Find path from start to end using BFS."""
        queue = [(start, [start])]
        visited = set()
        while queue:
            current, path = queue.pop(0)
            if current == end:
                return path
            for neighbor in self.graph.zones[current].neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

    def run(self):
        if not self.is_reachable():
            raise ValueError(f"End hub '{self.end}' is not reachable from "
                             f"start hub '{self.start}'.")

        # Output path planning
        shortest_path = self.find_path(self.start, self.end)
        path_cost = 0
        for i in range(1, len(shortest_path)):
            to_zone = shortest_path[i]
            if self.graph.zones[to_zone].zone_type == "restricted":
                path_cost += 2
            else:
                path_cost += 1
        print(f"[Path Planning] Shortest path (cost={path_cost}): " +
              " → ".join(shortest_path))
        print()

        drones = list(self.drones)
        for drone in drones:
            drone.in_flight = None  # (from_zone, to_zone, steps_left)

        delivered = set()
        turn = 0
        total_moves = 0

        while len(delivered) < len(drones):
            turn += 1
            used_links = set()
            moves_this_turn = []  # Will contain (drone_id, move_str) for order

            just_landed = set()  # Drones that landed (arrived) this turn

            # 1. Progress all in-flight drones: landings
            for drone in drones:
                if drone.drone_id in delivered:
                    continue
                if drone.in_flight:
                    from_zone, to_zone, steps_left = drone.in_flight
                    steps_left -= 1
                    if steps_left == 0:
                        drone.current_zone = to_zone
                        drone.in_flight = None
                        # Colorize arrival zone
                        moves_this_turn.append(
                            (drone.drone_id, f"D{drone.drone_id}-{self.colorize_zone(to_zone)}"))
                        just_landed.add(drone.drone_id)
                        total_moves += 1
                        if to_zone == self.end:
                            delivered.add(drone.drone_id)
                    else:
                        drone.in_flight = (from_zone, to_zone, steps_left)

            # 2. For all drones NOT delivered, NOT in-flight, and NOT just landed, try to move
            for drone in drones:
                if (drone.drone_id in delivered or
                   drone.in_flight or drone.drone_id in just_landed):
                    continue
                if drone.current_zone == self.end:
                    delivered.add(drone.drone_id)
                    continue
                path = self.find_path(drone.current_zone, self.end)
                if len(path) > 1:
                    from_zone = path[0]
                    to_zone = path[1]
                    link = (from_zone, to_zone)
                    if link in used_links:
                        continue  # Only one new departure per connection per turn
                    used_links.add(link)
                    if self.graph.zones[to_zone].zone_type == "restricted":
                        drone.in_flight = (from_zone, to_zone, 1)  # Arrives next turn
                        # Colorize
                        moves_this_turn.append(
                            (drone.drone_id,
                             f"D{drone.drone_id}-{self.colorize_zone(from_zone)}-{self.colorize_zone(to_zone)}"))
                        total_moves += 1
                    else:
                        drone.current_zone = to_zone
                        moves_this_turn.append(
                            (drone.drone_id, f"D{drone.drone_id}-{self.colorize_zone(to_zone)}"))
                        total_moves += 1
                        if to_zone == self.end:
                            delivered.add(drone.drone_id)
                else:
                    delivered.add(drone.drone_id)

            # Order all move events by drone_id
            if moves_this_turn:
                moves_this_turn.sort()
                print(f"Turn {turn}: {' '.join(m for _, m in moves_this_turn)}")

        print()
        print(f"Total turns: {turn}")
        print(f"Total moves: {total_moves}")
        print(f"Avg moves/turn: {total_moves/turn:.2f}")
        print(f"Avg turns/drone: {turn/len(drones):.2f}")
        print(f"Total path cost: {total_moves}")
