import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.vehicle_state import VehicleState


class VehicleStateManager:
    """ Synchronizes all active SUMO vehicles with the Python SimulationState. """

    def __init__(self, simulation_state: SimulationState):
        self.simulation_state = simulation_state

    def synchronize_with_sumo(self) -> list[str]:
        """
        Synchronize every active SUMO vehicle.

        Returns:
            List of vehicle IDs currently active in SUMO.
        """

        active_vehicle_ids = traci.vehicle.getIDList()

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

        return list(active_vehicle_ids)