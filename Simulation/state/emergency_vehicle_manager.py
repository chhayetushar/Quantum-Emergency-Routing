from Simulation.state.emergency_vehicle_state import EmergencyVehicleState
from Simulation.state.simulation_state import SimulationState


class EmergencyVehicleManager:
    """
    Manages emergency vehicle states inside the simulation.
    """

    VALID_VEHICLE_TYPES = {
        "AMBULANCE",
        "POLICE",
        "FIRETRUCK"
    }

    def __init__(self, simulation_state: SimulationState):
        self.simulation_state = simulation_state

    def register_vehicle(
        self,
        vehicle_id: str,
        vehicle_type: str
    ) -> EmergencyVehicleState:

        if vehicle_id in self.simulation_state.emergency_vehicles:
            raise ValueError(
                f"Emergency vehicle '{vehicle_id}' already exists."
            )

        if vehicle_type not in self.VALID_VEHICLE_TYPES:
            raise ValueError(
                f"Invalid emergency vehicle type: {vehicle_type}"
            )

        vehicle = EmergencyVehicleState(
            vehicle_id=vehicle_id,
            vehicle_type=vehicle_type
        )

        self.simulation_state.emergency_vehicles[vehicle_id] = vehicle

        return vehicle