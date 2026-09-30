import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.traffic.road_state_updater import create_road_state
from Simulation.traffic.road_state_updater import update_road_states


class TrafficStateManager:
    """
    Manages road-level traffic state for the simulation.
    """

    def __init__(
        self,
        simulation_state: SimulationState
    ):
        self.simulation_state = simulation_state

    def discover_active_roads(
        self,
        max_roads: int | None = None
    ) -> list[str]:
        """
        Find SUMO edges that currently contain
        at least one vehicle.
        """

        active_road_ids = []

        edge_ids = traci.edge.getIDList()

        for edge_id in edge_ids:

            vehicle_count = (
                traci.edge.getLastStepVehicleNumber(
                    edge_id
                )
            )

            if vehicle_count > 0:

                active_road_ids.append(edge_id)

                if (
                    max_roads is not None
                    and len(active_road_ids) >= max_roads
                ):
                    break

        return active_road_ids

    def initialize_roads(
        self,
        edge_ids: list[str]
    ) -> None:
        """
        Create RoadState objects for the supplied
        SUMO edges.
        """

        for edge_id in edge_ids:

            if edge_id in self.simulation_state.roads:
                continue

            try:

                road_state = create_road_state(
                    edge_id
                )

                self.simulation_state.roads[
                    edge_id
                ] = road_state

            except ValueError:

                continue

    def discover_and_initialize_active_roads(
        self,
        max_roads: int | None = None
    ) -> list[str]:
        """
        Discover active roads and initialize only
        roads that are not already stored.
        """

        active_road_ids = self.discover_active_roads(
            max_roads=max_roads
        )

        new_road_ids = []

        for road_id in active_road_ids:

            if road_id in self.simulation_state.roads:
                continue

            try:

                road_state = create_road_state(
                    road_id
                )

                self.simulation_state.roads[
                    road_id
                ] = road_state

                new_road_ids.append(road_id)

            except ValueError:

                continue

        return new_road_ids

    def update_roads(self) -> None:
        """
        Update dynamic traffic information for all
        roads stored in SimulationState.
        """

        update_road_states(
            self.simulation_state.roads
        )

    def synchronize(
        self,
        max_new_roads: int | None = None
    ) -> list[str]:
        """
        Perform one complete traffic-state
        synchronization cycle.

        Returns
        -------
        list[str]
            Road IDs that were newly discovered
            and initialized during this cycle.
        """

        new_road_ids = (
            self.discover_and_initialize_active_roads(
                max_roads=max_new_roads
            )
        )

        self.update_roads()

        return new_road_ids

    def step(
        self,
        max_new_roads: int | None = None
    ) -> list[str]:
        """
        Advance the SUMO simulation by one step and
        synchronize the traffic state.

        Returns
        -------
        list[str]
            Road IDs that were newly discovered and initialized.
        """

        # Advance SUMO simulation
        traci.simulationStep()

        # Update central simulation time
        self.simulation_state.simulation_time = (
            traci.simulation.getTime()
        )

        # Discover, initialize, and update roads
        new_road_ids = self.synchronize(
            max_new_roads=max_new_roads
        )

        return new_road_ids