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

    def colorize_zone(self, zone_name: str) -> str:
        """Apply color to zone name if defined in map."""
        color = self.graph.zones[zone_name].color
        if color and color.lower() in COLOR_MAP:
            return f"{COLOR_MAP[color.lower()]}{zone_name}{RESET}"
        return zone_name

    def find_path(self, start: str, end: str) -> list[str]:
        """Find path from start to end using BFS."""
        queue = [(start, [start])]
        visited = set()
        while queue:
            current, path = queue.pop(0)
            if current == end:
                return path
            neighbors = list(self.graph.zones[current].neighbors)
            neighbors.sort(key=lambda n:
                           self.graph.zones[n].zone_type != "priority")
            for neighbor in neighbors:
                zone_type = self.graph.zones[neighbor].zone_type
                if neighbor not in visited and zone_type != "blocked":
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        raise ValueError(f"End hub '{self.end}' is not reachable from "
                         f"start hub '{self.start}'.")

    def run(self) -> None:
        """Run the simulation, moving drones from start to end
                while respecting all constraints."""
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
            drone.in_flight = None

        delivered: set[int] = set()
        turn = 0
        total_moves = 0

        while len(delivered) < len(drones):
            turn += 1
            moves_this_turn = []
            just_landed = set()

            # Step 1: Track how many drones are currently in each zone
            zone_occupancy = {z: 0 for z in self.graph.zones}
            for drone in drones:
                if drone.drone_id not in delivered and drone.in_flight is None:
                    zone_occupancy[drone.current_zone] += 1

            # Step 2: Land all drones in flight (restricted arrivals)
            for drone in drones:
                if drone.drone_id in delivered:
                    continue
                if drone.in_flight:
                    from_zone, to_zone, steps_left = drone.in_flight
                    steps_left -= 1
                    if steps_left == 0:
                        drone.current_zone = to_zone
                        drone.in_flight = None
                        moves_this_turn.append(
                            (drone.drone_id, f"D{drone.drone_id}-"
                                             f"{self.colorize_zone(to_zone)}"))
                        just_landed.add(drone.drone_id)
                        total_moves += 1
                        if to_zone == self.end:
                            delivered.add(drone.drone_id)
                    else:
                        drone.in_flight = (from_zone, to_zone, steps_left)

            # Step 3: PLANNING: mark planned moves this turn
            planned_moves: list[tuple[Drone, str, str, bool]] = []
            planned_links: dict[tuple[str, str], list[Drone]] = {}
            planned_arrivals: dict[str, list[Drone]] = {}
            for drone in drones:
                if (
                    drone.drone_id in delivered
                    or drone.in_flight
                    or drone.drone_id in just_landed
                    or drone.current_zone == self.end
                ):
                    continue
                path = self.find_path(drone.current_zone, self.end)
                if len(path) > 1:
                    from_zone = path[0]
                    to_zone = path[1]
                    is_restricted = (self.graph.zones[to_zone].zone_type
                                     == "restricted")
                    planned_moves.append((drone, from_zone,
                                          to_zone, is_restricted))
                    link = (from_zone, to_zone)
                    planned_links.setdefault(link, []).append(drone)
                    planned_arrivals.setdefault(to_zone, []).append(drone)

            # Step 4: Sort requests (lowest drone_id first for fairness)
            for key in planned_links:
                planned_links[key].sort(key=lambda d: d.drone_id)
            for zone in planned_arrivals:
                planned_arrivals[zone].sort(key=lambda d: d.drone_id)

            # ----------- PIPELINING LOGIC -------------- #
            # Count how many leave each zone (for pipelining)
            zone_leaving = {z: 0 for z in self.graph.zones}
            for drone, from_zone, to_zone, is_restricted in planned_moves:
                zone_leaving[from_zone] += 1

            # Step 5: Enforce capacities, select allowed ones only
            allowed_moves: set[Drone] = set()
            connection_usage: dict[tuple[str, str], int] = {}
            zone_incoming: dict[str, int] = {}
            for drone, from_zone, to_zone, is_restricted in planned_moves:
                link = (from_zone, to_zone)
                # Get max_link_capacity between from_zone and to_zone
                conn = self.graph.zones[from_zone].neighbors[to_zone]
                max_link = getattr(conn, "max_link_capacity", 1)
                connection_usage.setdefault(link, 0)
                if connection_usage[link] >= max_link:
                    continue  # skip, link is full

                max_drones = getattr(self.graph.zones[to_zone],
                                     "max_drones", 1)
                zone_incoming.setdefault(to_zone, 0)
                # Only enforce max_drones for zones other than start/end
                if to_zone != self.start and to_zone != self.end:
                    projected = (zone_occupancy[to_zone]
                                 + zone_incoming[to_zone]
                                 - zone_leaving.get(to_zone, 0))
                    if projected >= max_drones:
                        continue  # skip, zone is full (with pipelining!)

                allowed_moves.add(drone)
                connection_usage[link] += 1
                zone_incoming[to_zone] += 1

            # Step 6: Actually perform allowed moves
            for drone, from_zone, to_zone, is_restricted in planned_moves:
                if drone not in allowed_moves:
                    continue  # Drone must wait this turn!
                if is_restricted:
                    drone.in_flight = (from_zone, to_zone, 1)
                    moves_this_turn.append(
                        (drone.drone_id,
                         f"D{drone.drone_id}-{self.colorize_zone(from_zone)}-"
                         f"{self.colorize_zone(to_zone)}"))
                    total_moves += 1
                else:
                    drone.current_zone = to_zone
                    moves_this_turn.append(
                        (drone.drone_id, f"D{drone.drone_id}-"
                         f"{self.colorize_zone(to_zone)}"))
                    total_moves += 1
                    if to_zone == self.end:
                        delivered.add(drone.drone_id)

            # Output all move events this turn, sorted by drone_id
            if moves_this_turn:
                moves_this_turn.sort()
                print(f"Turn{turn}: {' '.join(m for _, m in moves_this_turn)}")

        print()
        print(f"Total turns: {turn}")
        print(f"Total moves: {total_moves}")
        print(f"Avg moves/turn: {total_moves/turn:.2f}")
        print(f"Avg turns/drone: {turn/len(drones):.2f}")
        print(f"Total path cost: {total_moves}")
