from typing import Optional, Dict
from connection import Connection


class Zone:
    """
    Represents a zone (hub) in the drone map.
    """
    def __init__(self, name: str, x: int, y: int, zone_type: str = "normal",
                 color: Optional[str] = None, max_drones: int = 1):
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.color: Optional[str] = color
        self.max_drones: int = max_drones
        self.neighbors: Dict[str, "Connection"] = {}

    def __repr__(self) -> str:
        return (f"Zone({self.name}, type={self.zone_type},"
                f"max_drones={self.max_drones})")
