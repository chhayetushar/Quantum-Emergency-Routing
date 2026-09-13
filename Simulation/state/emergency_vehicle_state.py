from dataclasses import dataclass
from typing import Optional


@dataclass
class EmergencyVehicleState:
    """
    Represents the current operational state of an emergency vehicle.
    """

    vehicle_id: str
    vehicle_type: str

    current_edge: Optional[str] = None
    speed: float = 0.0
    position: float = 0.0

    status: str = "AVAILABLE"

    assigned_emergency: Optional[str] = None