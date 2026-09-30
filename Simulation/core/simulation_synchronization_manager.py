import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.vehicle_state_manager import VehicleStateManager
from Simulation.emergency.emergency_vehicle_manager import (
    EmergencyVehicleManager
)
from Simulation.traffic.traffic_state_manager import (
    TrafficStateManager
)


class SimulationSynchronizationManager:
    """
    Coordinates one complete SUMO -> Python
    synchronization cycle.
    """

    def __init__(
        self,
        simulation_state: SimulationState
    ):
        self.simulation_state = simulation_state

        self.vehicle_manager = VehicleStateManager(
            simulation_state
        )

        self.emergency_vehicle_manager = (
            EmergencyVehicleManager(
                simulation_state
            )
        )

        self.traffic_manager = TrafficStateManager(
            simulation_state
        )

    def step(
        self,
        max_new_roads: int | None = None
    ) -> dict[str, object]:
        """
        Advance SUMO by one step and synchronize
        all major simulation state components.

        Returns:
            Synchronization information for this step.
        """

        # --------------------------------------------------
        # 1. Advance SUMO exactly once
        # --------------------------------------------------

        traci.simulationStep()

        # --------------------------------------------------
        # 2. Synchronize central simulation time
        # --------------------------------------------------

        self.simulation_state.simulation_time = (
            traci.simulation.getTime()
        )

        # --------------------------------------------------
        # 3. Synchronize ALL vehicles
        # --------------------------------------------------

        active_vehicle_ids = (
            self.vehicle_manager.synchronize_with_sumo()
        )

        # --------------------------------------------------
        # 4. Synchronize emergency vehicles
        # --------------------------------------------------

        emergency_vehicle_ids = (
            self.emergency_vehicle_manager
            .synchronize_with_sumo()
        )

        # --------------------------------------------------
        # 5. Synchronize road traffic state
        # --------------------------------------------------

        new_road_ids = (
            self.traffic_manager.synchronize(
                max_new_roads=max_new_roads
            )
        )

        # --------------------------------------------------
        # Return synchronization result
        # --------------------------------------------------

        return {
            "simulation_time": (
                self.simulation_state.simulation_time
            ),
            "active_vehicle_ids": active_vehicle_ids,
            "emergency_vehicle_ids": emergency_vehicle_ids,
            "new_road_ids": new_road_ids
        }