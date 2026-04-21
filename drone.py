from typing import List


class Drone:
    """
    Represents a drone in the system.
    """
    def __init__(self, drone_id: int, current_zone: str) -> None:
        self.drone_id: int = drone_id
        self.current_zone: str = current_zone
        self.path: List[str] = []
        self.state: str = "waiting"

    def __repr__(self) -> str:
        return f"Drone(D{self.drone_id} at {self.current_zone})"
