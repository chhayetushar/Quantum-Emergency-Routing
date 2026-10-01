import traci

from Simulation.state.emergency_state import EmergencyState
from Simulation.state.simulation_state import SimulationState

from Simulation.state.emergency_vehicle_manager import (
    EmergencyVehicleManager
)

from Simulation.routing.road_graph import RoadGraph
from Simulation.routing.emergency_response_router import (
    EmergencyResponseRouter
)


SUMO_BINARY = (
    r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"
)

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def find_emergency_destination_edge(
    graph: RoadGraph,
    start_edge_id: str,
    hops: int = 5
) -> str:
    """
    Find a connected edge several hops away from
    the vehicle's current edge.
    """

    current_edge = graph.edges.get(
        start_edge_id
    )

    if current_edge is None:
        raise ValueError(
            f"Starting edge '{start_edge_id}' "
            f"does not exist."
        )

    current_node = current_edge.to_node

    visited_nodes = {
        current_node
    }

    destination_edge = None

    for _ in range(hops):

        outgoing_edges = graph.get_neighbors(
            current_node
        )

        next_edge = None

        for edge in outgoing_edges:

            if edge.to_node not in visited_nodes:
                next_edge = edge
                break

        if next_edge is None:
            break

        destination_edge = next_edge

        current_node = next_edge.to_node

        visited_nodes.add(
            current_node
        )

    if destination_edge is None:
        raise ValueError(
            "Could not find a connected emergency "
            "destination edge."
        )

    return destination_edge.edge_id


def test_real_emergency_response_router():

    simulation_state = SimulationState()

    emergency_vehicle_manager = (
        EmergencyVehicleManager(
            simulation_state
        )
    )

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:

        # --------------------------------------------------
        # Build real SUMO road graph
        # --------------------------------------------------

        graph = RoadGraph()

        graph.build_from_sumo()

        print(
            f"Graph nodes: "
            f"{graph.node_count()}"
        )

        print(
            f"Graph edges: "
            f"{graph.edge_count()}"
        )

        # --------------------------------------------------
        # Wait for a real emergency vehicle
        # --------------------------------------------------

        emergency_vehicle_id = None

        for _ in range(300):

            traci.simulationStep()

            emergency_vehicle_ids = (
                emergency_vehicle_manager
                .synchronize_with_sumo()
            )

            if emergency_vehicle_ids:

                emergency_vehicle_id = (
                    emergency_vehicle_ids[0]
                )

                break

        assert emergency_vehicle_id is not None

        # --------------------------------------------------
        # Get synchronized emergency vehicle
        # --------------------------------------------------

        vehicle = (
            simulation_state.emergency_vehicles[
                emergency_vehicle_id
            ]
        )

        assert vehicle.current_edge is not None

        print(
            f"\nEmergency vehicle: "
            f"{vehicle.vehicle_id}"
        )

        print(
            f"Vehicle type: "
            f"{vehicle.vehicle_type}"
        )

        print(
            f"Current edge: "
            f"{vehicle.current_edge}"
        )

        # --------------------------------------------------
        # Select a reachable emergency location
        # --------------------------------------------------

        emergency_edge_id = (
            find_emergency_destination_edge(
                graph,
                vehicle.current_edge,
                hops=5
            )
        )

        print(
            f"Emergency edge: "
            f"{emergency_edge_id}"
        )

        # --------------------------------------------------
        # Create emergency state
        # --------------------------------------------------

        emergency = EmergencyState(
            emergency_id="E001",
            emergency_type="ACCIDENT",
            location=emergency_edge_id,
            severity="HIGH",
            creation_time=(
                traci.simulation.getTime()
            ),
            status="WAITING"
        )

        simulation_state.emergencies[
            "E001"
        ] = emergency

        # --------------------------------------------------
        # Create response router
        # --------------------------------------------------

        response_router = (
            EmergencyResponseRouter(
                simulation_state,
                graph
            )
        )

        # --------------------------------------------------
        # Calculate emergency route
        # --------------------------------------------------

        route, total_distance = (
            response_router.plan_route(
                vehicle_id=emergency_vehicle_id,
                emergency_id="E001"
            )
        )

        route_ids = [
            edge.edge_id
            for edge in route
        ]

        print(
            f"\nEmergency route edges: "
            f"{len(route)}"
        )

        print(
            f"Emergency route distance: "
            f"{total_distance}"
        )

        print(
            "\nEmergency route:"
        )

        for edge_id in route_ids:

            print(
                edge_id
            )

        # --------------------------------------------------
        # Validate route
        # --------------------------------------------------

        assert len(route) >= 2

        # Must start with vehicle's current edge
        assert (
            route[0].edge_id
            == vehicle.current_edge
        )

        # Must end on emergency edge
        assert (
            route[-1].edge_id
            == emergency.location
        )

        # Route must be connected
        for index in range(
            len(route) - 1
        ):

            assert (
                route[index].to_node
                == route[index + 1].from_node
            )

        # Distance must equal edge-distance sum
        calculated_distance = sum(
            edge.distance
            for edge in route
        )

        assert abs(
            calculated_distance
            - total_distance
        ) < 1e-9

        print(
            "\nReal emergency response route "
            "validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    test_real_emergency_response_router()