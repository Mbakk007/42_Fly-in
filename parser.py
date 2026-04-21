from typing import Tuple
from zone import Zone
from graph import GraphModel


class ParseError(Exception):
    """Custom exception for parsing errors."""
    pass


ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


def parse_metadata(metadata: str, line_num: int) -> dict:
    """
    Parse metadata enclosed in [] on lines, e.g. [zone=restricted color=red]
    """
    meta = {}
    try:
        content = metadata.strip("[]").strip()
        for item in content.split():
            if '=' in item:
                k, v = item.split("=", 1)
                meta[k.strip()] = v.strip()
    except Exception:
        raise ParseError(f"Line {line_num}: Invalid metadata format "
                         f"'{metadata}'")
    return meta


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

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.split("#")[0].strip()
            if not line:
                continue

            if line.startswith("nb_drones:"):
                if nb_drones is not None:
                    raise ParseError(f"Line {line_num}: nb_drones already"
                                     f" defined")
                try:
                    nb_drones = int(line.split(":")[1].strip())
                    if nb_drones <= 0:
                        raise ValueError()
                except Exception:
                    raise ParseError(f"Line {line_num}: Invalid nb_drone "
                                     f"value")

            if line.startswith("start_hub:"):
                v = line.split(":", 1)[1].strip()
                k = v.split("[", 1)
                data_part = k[0].strip()
                meta_part = f"[{k[1]}]" if len(k) == 2 else ""
                parts = data_part.split()
                if len(parts) != 3:
                    raise ParseError(f"Line {line_num}: Invalid start_hub"
                                     f" definition")
                name, x_str, y_str = parts
                if '-' in name or ' ' in name:
                    raise ParseError(f"Line {line_num}: Zone names cannot "
                                     f"have dashes or spaces: {name}")
                x = int(x_str)
                y = int(y_str)

                metadata = {}
                if meta_part:
                    metadata = parse_metadata(meta_part, line_num)
                zone_type = metadata.get("zone", "normal")
                color = metadata.get("color")
                max_drones = int(metadata.get("max_drones", 1))
                if max_drones <= 0:
                    raise ParseError(f"Line {line_num}: max_drones must be "
                                     f"a positive integer")
                if zone_type not in ZONE_TYPES:
                    raise ParseError(f"Line {line_num}: Unknown zone type")
                if name in seen_zones:
                    raise ParseError(f"Line {line_num}: Duplicate zone name")
                seen_zones.add(name)
                zone = Zone(name, x, y, zone_type, color, max_drones)
                graph.add_zone(zone)
                if start_hub is not None:
                    raise ParseError(f"Line {line_num}:ERR multiple start_hub")
                start_hub = name

            if line.startswith("end_hub:"):
                v = line.split(":", 1)[1].strip()
                k = v.split("[", 1)
                data_part = k[0].strip()
                meta_part = f"[{k[1]}" if len(k) == 2 else ""
                parts = data_part.split()
                if len(parts) != 3:
                    raise ParseError(f"Line {line_num}: Invalid end_hub "
                                     f"definition")
                name, x_str, y_str = parts
                if '-' in name or ' ' in name:
                    raise ParseError(f"Line {line_num}: Zone names cannot "
                                     f"contain dashes or spaces: '{name}'")
                x = int(x_str)
                y = int(y_str)
                metadata = {}
                if meta_part:
                    metadata = parse_metadata(meta_part, line_num)
                zone_type = metadata.get("zone", "normal")
                color = metadata.get("color")
                max_drones = int(metadata.get("max_drones", 1))
                if max_drones <= 0:
                    raise ParseError(f"Line {line_num}: max_drones must be "
                                     f"a positive integer")
                if zone_type not in ZONE_TYPES:
                    raise ParseError(f"Line {line_num}: Unknown zone type")
                if name in seen_zones:
                    raise ParseError(f"Line {line_num}: Duplicate zone name")
                seen_zones.add(name)
                zone = Zone(name, x, y, zone_type, color, max_drones)
                graph.add_zone(zone)
                if end_hub is not None:
                    raise ParseError(f"Line {line_num}:ERR multiple end_hub")
                end_hub = name

            if line.startswith("hub:"):
                v = line.split(":", 1)[1].strip()
                k = v.split("[", 1)
                data_part = k[0].strip()
                meta_part = f"[{k[1]}" if len(k) == 2 else ""
                parts = data_part.split()
                if len(parts) != 3:
                    raise ParseError(f"Line {line_num}:Invalid hub definition")
                name, x_str, y_str = parts
                if '-' in name or ' ' in name:
                    raise ParseError(f"Line {line_num}: Zone names cannot "
                                     f"contain dashes or spaces: '{name}'")
                x = int(x_str)
                y = int(y_str)
                metadata = {}
                if meta_part:
                    metadata = parse_metadata(meta_part, line_num)
                zone_type = metadata.get("zone", "normal")
                color = metadata.get("color")
                max_drones = int(metadata.get("max_drones", 1))
                if max_drones <= 0:
                    raise ParseError(f"Line {line_num}: max_drones must be a "
                                     f"positive integer")
                if zone_type not in ZONE_TYPES:
                    raise ParseError(f"Line {line_num}: Unknown zone type")
                if name in seen_zones:
                    raise ParseError(f"Line {line_num}: Duplicate zone name")
                seen_zones.add(name)
                zone = Zone(name, x, y, zone_type, color, max_drones)
                graph.add_zone(zone)

            if line.startswith("connection:"):
                rest = line.split(":", 1)[1].strip()
                parts = rest.split()
                if len(parts) != 2:
                    raise ParseError(f"Line {line_num}: Invalid "
                                     f"connection format")
                src, dst = parts
                if src == dst:
                    raise ParseError(f"Line {line_num}: Connection from a zone"
                                     f" to itself is not allowed ({src})")
                if src not in seen_zones or dst not in seen_zones:
                    raise ParseError(f"Line {line_num}: Connection references "
                                     f"undefined zone(s): '{src}' or '{dst}'")
                connection = frozenset([src, dst])
                if connection in seen_connections:
                    raise ParseError(f"Line {line_num}: Duplicate connection "
                                     f"between '{src}' and '{dst}'")
                seen_connections.add(connection)
                graph.add_connection(src, dst)

    if nb_drones is None:
        raise ParseError("Missing 'nb_drones' line.")
    if start_hub is None:
        raise ParseError("Missing 'start_hub' zone.")
    if end_hub is None:
        raise ParseError("Missing 'end_hub' zone.")

    return nb_drones, graph, start_hub, end_hub
