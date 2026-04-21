import sys
from parser import parse_input_file, ParseError
from simulation import Simulation


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <map_file>")
        sys.exit(1)
    map_path = sys.argv[1]

    try:
        nb_drones, graph, start, end = parse_input_file(map_path)
    except ParseError as e:
        print(f"Error parsing input: {e}")
        sys.exit(1)

    print(f"Loaded map: {map_path}")
    print(f"Drones: {nb_drones}, Start: {start}, End: {end}")
    print("Initial network state:")

    for z in graph.zones:
        prefix = "[D" if z == start else "["
        suffix = "]" if z == end else "] "
        print(f"{prefix}{z}{suffix}", end="  ")
    print()

    sim = Simulation(nb_drones, graph, start, end)
    sim.run()


if __name__ == "__main__":
    main()
