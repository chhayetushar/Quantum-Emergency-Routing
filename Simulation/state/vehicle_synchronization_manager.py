from Simulation.state.simulation_state import SimulationState
from Simulation.state.vehicle_state_manager import VehicleStateManager
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


class VehicleSynchronizationManager:
    """
    Coordinates synchronization of all vehicles and
    emergency vehicles with the SUMO simulation.
    """

    def __init__(self, simulation_state: SimulationState):
        self.simulation_state = simulation_state

        self.vehicle_manager = VehicleStateManager(
            simulation_state
        )

        self.emergency_vehicle_manager = EmergencyVehicleManager(
            simulation_state
        )

    def synchronize(self) -> tuple[list[str], list[str]]:
        """
        Synchronize all vehicles and emergency vehicles.

        Returns:
            (
                all_active_vehicle_ids,
                active_emergency_vehicle_ids
            )
        """

        all_active_vehicle_ids = (
            self.vehicle_manager.synchronize_with_sumo()
        )

        active_emergency_vehicle_ids = (
            self.emergency_vehicle_manager.synchronize_with_sumo()
        )

        return (
            all_active_vehicle_ids,
            active_emergency_vehicle_ids
        )