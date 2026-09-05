from dataclasses import dataclass
from typing import Optional


@dataclass
class RoadState:
    road_id: str
    from_node: Optional[str] = None
    to_node: Optional[str] = None
    distance: float = 0.0
    speed_limit: float = 0.0
    current_speed: float = 0.0
    vehicle_count: int = 0
    travel_time: float = 0.0
    congestion_level: str = "UNKNOWN"
# Temporaly for testing purposes, we can create an instance of RoadState and print it to verify the implementation.
if __name__ == "__main__":
    road = RoadState(
        road_id="edge_105",
        from_node="junction_A",
        to_node="junction_B",
        distance=850.0,
        speed_limit=13.9,
        current_speed=6.2,
        vehicle_count=38,
        travel_time=137.0,
        congestion_level="HIGH"
    )

    print(road)