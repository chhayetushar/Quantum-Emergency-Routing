from dataclasses import dataclass, field
from typing import Dict

from .vehicle_state import VehicleState
from .road_state import RoadState
from .emergency_state import EmergencyState


@dataclass
class SimulationState:
    simulation_time: float = 0.0

    vehicles: Dict[str, VehicleState] = field(default_factory=dict)
    roads: Dict[str, RoadState] = field(default_factory=dict)
    emergencies: Dict[str, EmergencyState] = field(default_factory=dict)
## Temporarily for testing purposes, we can create an instance of SimulationState and print it to verify the implementation.
if __name__ == "__main__":
    state = SimulationState()

    print("Simulation Time:", state.simulation_time)
    print("Vehicles:", state.vehicles)
    print("Roads:", state.roads)
    print("Emergencies:", state.emergencies)