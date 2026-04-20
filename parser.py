from typing import Tuple
from zone import Zone
from connection import Connection
from graph import GraphModel
import re


class ParseError(Exception):
    """Custom exception for parsing errors."""
    pass


ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


def parse_metadata(metadata_raw: str, line_num: int) -> dict:
    """
    Parse metadata enclosed in [] on lines, e.g. [zone=restricted color=red]
    """
    metadata = {}
    try:
        content = metadata_raw.strip("[]").strip()
        for item in content.split():
            if '=' in item:
                k, v = item.split("=", 1)
                metadata[k.strip()] = v.strip()
    except Exception:
        raise ParseError(f"Line {line_num}: Invalid metadata format "
                         f"'{metadata_raw}'")
    return metadata


def parse_input_file(file_path: str) -> Tuple[int, GraphModel, str, str]:
    """
    Parse the input map file.
    Returns (nb_drones, graph, start_hub_name, end_hub_name)
    Raises ParseError on invalid input.
    """
    nb_drones = None
    graph = GraphModel()
    seen_zones = set()
    seen_connections = set()
    start_hub = None
    end_hub = None

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.split("#")[0].strip()
            if not line:
                continue

            # Drones count
            if line.startswith("nb_drones:"):
                if nb_drones is not None:
                    raise ParseError(f"Line {line_num}: nb_drones "
                                     f"already defined")
                try:
                    nb_drones = int(line.partition(":")[2].strip())
                    if nb_drones <= 0:
                        raise ValueError()
                except Exception:
                    raise ParseError(f"Line {line_num}: "
                                     f"Invalid nb_drones value")
                continue

            def zone_worker(typ, is_start=False, is_end=False):
                nonlocal start_hub, end_hub
                _, rest = line.split(":", 1)
                rest = rest.strip()
                # Split up to possible first [
                fields = rest.split("[", 1)
                data_part = fields[0].strip()
                meta_part = f"[{fields[1]}" if len(fields) == 2 else ""
                try:
                    parts = data_part.split()
                    if len(parts) != 3:
                        raise ParseError(f"Line {line_num}: Invalid {typ} "
                                         f"zone definition")

                    name, x_str, y_str = parts
                    if '-' in name or ' ' in name:
                        raise ParseError(f"Line {line_num}: Zone names cannot "
                                         f"contain dashes or spaces: '{name}'")
                    x, y = int(x_str), int(y_str)

                    metadata = {}
                    if meta_part:
                        if not (meta_part.startswith("[")
                                and meta_part.endswith("]")):
                            raise ParseError(f"Line {line_num}: "
                                             f"Malformed metadata brackets")
                        metadata = parse_metadata(meta_part, line_num)

                    zone_type = metadata.get("zone", "normal")
                    if zone_type not in ZONE_TYPES:
                        raise ParseError(f"Line {line_num}: "
                                         f"Unknown zone type '{zone_type}'")
                    color = metadata.get("color")
                    max_drones = int(metadata.get("max_drones", 1))
                    if max_drones <= 0:
                        raise ParseError(f"Line {line_num}: max_drones "
                                         f"must be a positive integer")
                    zone = Zone(name, x, y, zone_type, color, max_drones)
                    if name in seen_zones:
                        raise ParseError(f"Line {line_num}: "
                                         f"Duplicate zone name '{name}'")
                    seen_zones.add(name)
                    graph.add_zone(zone)
                    if is_start:
                        if start_hub is not None:
                            raise ParseError(f"Line {line_num}: "
                                             f"Multiple start_hub detected")
                        start_hub = name
                    if is_end:
                        if end_hub is not None:
                            raise ParseError(f"Line {line_num}: "
                                             f"Multiple end_hub detected")
                        end_hub = name
                except ParseError:
                    raise
                except Exception as e:
                    raise ParseError(f"Line {line_num}: "
                                     f"Invalid zone definition: {e}")

            # Start/End/Hub
            if line.startswith("start_hub:"):
                zone_worker("start", is_start=True)
                continue
            if line.startswith("end_hub:"):
                zone_worker("end", is_end=True)
                continue
            if line.startswith("hub:"):
                zone_worker("hub")
                continue

            # Connections
            if line.startswith("connection:"):
                _, rest = line.split(":", 1)
                rest = rest.strip()
                # Expect <zone1>-<zone2> [metadata]
                match = re.match(r"(\S+)-(\S+)(.*)", rest)
                if not match:
                    raise ParseError(f"Line {line_num}: "
                                     f"Invalid connection definition")
                zone1, zone2, meta_part = match.groups()
                if ((' ' in zone1 or '-' in zone1) or
                   (' ' in zone2 or '-' in zone2)):
                    raise ParseError(f"Line {line_num}: "
                                     f"Connection zone names cannot contain da"
                                     f"shes or spaces: '{zone1}' or '{zone2}'")
                if zone1 not in graph.zones or zone2 not in graph.zones:
                    raise ParseError(f"Line {line_num}: "
                                     f"Connection references "
                                     f"unknown zones '{zone1}' or '{zone2}'")

                metadata = {}
                meta_part = meta_part.strip()
                if meta_part:
                    if not (meta_part.startswith("[")
                            and meta_part.endswith("]")):
                        raise ParseError(f"Line {line_num}: Malformed "
                                         f"metadata brackets in connection")
                    metadata = parse_metadata(meta_part, line_num)
                max_link_capacity = int(metadata.get("max_link_capacity", 1))
                if max_link_capacity <= 0:
                    raise ParseError(f"Line {line_num}: max_link_capacity "
                                     f"must be positive")
                key = frozenset([zone1, zone2])
                if key in seen_connections:
                    raise ParseError(f"Line {line_num}: Duplicate "
                                     f"connection '{zone1}-{zone2}'")
                seen_connections.add(key)
                conn = Connection(zone1, zone2, max_link_capacity)
                graph.add_connection(conn)
                continue

            raise ParseError(f"Line {line_num}: Unknown or "
                             f"malformed line: {line}")

    # Final validations
    if nb_drones is None:
        raise ParseError("Missing 'nb_drones' definition")
    if start_hub is None:
        raise ParseError("Missing or invalid 'start_hub' zone")
    if end_hub is None:
        raise ParseError("Missing or invalid 'end_hub' zone")
    if len(graph.zones) < 2:
        raise ParseError("Need at least start and end zones")

    return nb_drones, graph, start_hub, end_hub
