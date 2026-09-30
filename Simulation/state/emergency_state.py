from dataclasses import dataclass
from typing import Optional


@dataclass
class EmergencyState:
    emergency_id: str
    emergency_type: str
    location: str
    severity: str
    creation_time: float
    status: str = "WAITING"
    assigned_vehicle: Optional[str] = None
# Temporarily for testing purposes, we can create an instance of EmergencyState and print it to verify the implementation.
if __name__ == "__main__":
    emergency = EmergencyState(
        emergency_id="EMG_001",
        emergency_type="MEDICAL",
        location="junction_452",
        severity="HIGH",
        creation_time=1250.0
    )

    print(emergency)