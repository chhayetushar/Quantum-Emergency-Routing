import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.vehicle_state import VehicleState


class VehicleStateManager:
    """
    Synchronizes vehicle states between SUMO and Python.
    """

    def __init__(self, simulation_state: SimulationState):
        self.simulation_state = simulation_state

    def synchronize_with_sumo(self) -> list[str]:
        """
        Synchronize every active SUMO vehicle.

        Vehicles currently present in SUMO are marked ACTIVE.
        Vehicles previously tracked but no longer present in SUMO
        are marked INACTIVE.

        Returns:
            List of vehicle IDs currently active in SUMO.
        """

        active_vehicle_ids = traci.vehicle.getIDList()
        active_vehicle_id_set = set(active_vehicle_ids)

        # ---------------------------------------------------------
        # 1. Create or update every currently active SUMO vehicle
        # ---------------------------------------------------------

        for vehicle_id in active_vehicle_ids:

            vehicle_type = traci.vehicle.getTypeID(
                vehicle_id
            )

            current_edge = traci.vehicle.getRoadID(
                vehicle_id
            )

            speed = traci.vehicle.getSpeed(
                vehicle_id
            )

            position = traci.vehicle.getLanePosition(
                vehicle_id
            )

            if vehicle_id not in self.simulation_state.vehicles:

                vehicle = VehicleState(
                    vehicle_id=vehicle_id,
                    vehicle_type=vehicle_type,
                    current_edge=current_edge,
                    speed=speed,
                    position=position,
                    status="ACTIVE"
                )

                self.simulation_state.vehicles[
                    vehicle_id
                ] = vehicle

            else:

                vehicle = self.simulation_state.vehicles[
                    vehicle_id
                ]

                vehicle.vehicle_type = vehicle_type
                vehicle.current_edge = current_edge
                vehicle.speed = speed
                vehicle.position = position
                vehicle.status = "ACTIVE"

        # ---------------------------------------------------------
        # 2. Mark previously tracked vehicles as INACTIVE
        #    when they are no longer present in SUMO
        # ---------------------------------------------------------

        for vehicle_id, vehicle in (
            self.simulation_state.vehicles.items()
        ):

            if vehicle_id not in active_vehicle_id_set:
                vehicle.status = "INACTIVE"

        return list(active_vehicle_ids)