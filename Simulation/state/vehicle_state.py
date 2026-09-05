from dataclasses import dataclass
from typing import Optional


@dataclass
class VehicleState:
    vehicle_id: str
    vehicle_type: str
    current_edge: Optional[str] = None
    speed: float = 0.0
    position: float = 0.0
    status: str = "UNKNOWN"

#temporaliry 
if __name__ == "__main__":
    vehicle = VehicleState(
        vehicle_id="ambulance_01",
        vehicle_type="ambulance",
        current_edge="edge_105",
        speed=12.5,
        position=235.4,
        status="AVAILABLE"
    )

    print(vehicle)