class Connection:
    """
    Represents a bidirectional connection between two zones.
    """
    def __init__(self, zone1: str, zone2: str, max_link_capacity: int = 1):
        self.zone1: str = zone1
        self.zone2: str = zone2
        self.max_link_capacity: int = max_link_capacity

    def __repr__(self) -> str:
        return (f"Connection({self.zone1}<->{self.zone2},"
                f"cap={self.max_link_capacity})")

    def other(self, name: str) -> str:
        """Return the name of the zone on the other end of this connection."""
        if name == self.zone1:
            return self.zone2
        if name == self.zone2:
            return self.zone1
        raise ValueError(f"Zone {name} not part of connection {self}")
