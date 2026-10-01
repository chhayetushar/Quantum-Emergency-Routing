from Simulation.state.emergency_state import EmergencyState
from Simulation.state.emergency_vehicle_state import EmergencyVehicleState
from Simulation.state.simulation_state import SimulationState

from Simulation.routing.road_graph import GraphEdge, RoadGraph
from Simulation.routing.emergency_route_planner import (
    EmergencyRoutePlanner
)


class EmergencyResponseRouter:
    """
    Connects SimulationState emergency information
    with the emergency route planner.
    """

    def __init__(
        self,
        simulation_state: SimulationState,
        graph: RoadGraph
    ):
        self.simulation_state = simulation_state
        self.graph = graph

        self.route_planner = EmergencyRoutePlanner(
            graph
        )

    def plan_route(
        self,
        vehicle_id: str,
        emergency_id: str
    ) -> tuple[list[GraphEdge], float]:
        """
        Calculate a route for an emergency vehicle
        to an emergency location.
        """

        # --------------------------------------------------
        # Validate emergency vehicle
        # --------------------------------------------------

        if vehicle_id not in (
            self.simulation_state.emergency_vehicles
        ):
            raise ValueError(
                f"Emergency vehicle '{vehicle_id}' "
                f"does not exist."
            )

        # --------------------------------------------------
        # Validate emergency
        # --------------------------------------------------

        if emergency_id not in (
            self.simulation_state.emergencies
        ):
            raise ValueError(
                f"Emergency '{emergency_id}' "
                f"does not exist."
            )

        # --------------------------------------------------
        # Get states
        # --------------------------------------------------

        vehicle = (
            self.simulation_state.emergency_vehicles[
                vehicle_id
            ]
        )

        emergency = (
            self.simulation_state.emergencies[
                emergency_id
            ]
        )

        # --------------------------------------------------
        # Validate vehicle location
        # --------------------------------------------------

        if not vehicle.current_edge:
            raise ValueError(
                f"Emergency vehicle '{vehicle_id}' "
                f"has no current edge."
            )

        # --------------------------------------------------
        # Validate emergency location
        # --------------------------------------------------

        if not emergency.location:
            raise ValueError(
                f"Emergency '{emergency_id}' "
                f"has no location."
            )

        # --------------------------------------------------
        # Calculate route
        # --------------------------------------------------

        return self.route_planner.plan_route(
            vehicle_edge_id=vehicle.current_edge,
            emergency_edge_id=emergency.location
        )