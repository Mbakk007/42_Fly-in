from typing import Dict
from zone import Zone
from connection import Connection


class GraphModel:
    """
    Represents the network graph of zones and connections.
    """
    def __init__(self):
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[frozenset, Connection] = {}

    def add_zone(self, zone: Zone):
        if zone.name in self.zones:
            raise ValueError(f"Duplicate zone detected: {zone.name}")
        self.zones[zone.name] = zone

    def add_connection(self, con: Connection):
        k = frozenset([con.zone1, con.zone2])
        if k in self.connections:
            raise ValueError(f"Duplicate connection detected:"
                             f" {con.zone1}-{con.zone2}")
        self.connections[k] = con
        self.zones[con.zone1].neighbors[con.zone2] = con
        self.zones[con.zone2].neighbors[con.zone1] = con
