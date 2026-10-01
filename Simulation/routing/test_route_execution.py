import traci

from Simulation.routing.road_graph import RoadGraph
from Simulation.routing.dijkstra_router import DijkstraRouter
from Simulation.routing.route_converter import RouteConverter


SUMO_BINARY = (
    r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"
)

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def find_test_route(
    graph: RoadGraph,
    current_edge_id: str,
    hop_count: int = 5
):
    """
    Find a reachable destination starting from the
    vehicle's current edge.
    """

    current_edge = graph.edges.get(
        current_edge_id
    )

    if current_edge is None:
        raise ValueError(
            f"Current edge '{current_edge_id}' "
            f"is not present in the graph."
        )

    source_node = current_edge.to_node
    current_node = source_node

    visited = {
        current_node
    }

    destination_node = None

    for _ in range(hop_count):

        outgoing_edges = graph.get_neighbors(
            current_node
        )

        next_edge = None

        for edge in outgoing_edges:

            if edge.to_node not in visited:

                next_edge = edge
                break

        if next_edge is None:
            break

        current_node = next_edge.to_node

        visited.add(
            current_node
        )

        destination_node = current_node

    if destination_node is None:
        raise ValueError(
            "Could not find a reachable destination."
        )

    return current_edge, source_node, destination_node


def test_route_execution():

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:

        # --------------------------------------------------
        # Build routing graph
        # --------------------------------------------------

        graph = RoadGraph()

        graph.build_from_sumo()

        router = DijkstraRouter(
            graph
        )

        # --------------------------------------------------
        # Find an active vehicle
        # --------------------------------------------------

        vehicle_id = None
        current_edge_id = None

        for _ in range(10):

            traci.simulationStep()

            active_vehicle_ids = (
                traci.vehicle.getIDList()
            )

            for candidate_vehicle_id in active_vehicle_ids:

                candidate_edge_id = (
                    traci.vehicle.getRoadID(
                        candidate_vehicle_id
                    )
                )

                if candidate_edge_id.startswith(":"):
                    continue

                if candidate_edge_id not in graph.edges:
                    continue

                vehicle_id = candidate_vehicle_id
                current_edge_id = candidate_edge_id
                break

            if vehicle_id is not None:
                break

        assert vehicle_id is not None
        assert current_edge_id is not None

        print(
            f"Vehicle ID: {vehicle_id}"
        )

        print(
            f"Initial edge: {current_edge_id}"
        )

        # --------------------------------------------------
        # Find destination
        # --------------------------------------------------

        (
            current_edge,
            source_node,
            destination_node
        ) = find_test_route(
            graph,
            current_edge_id
        )

        # --------------------------------------------------
        # Calculate route
        # --------------------------------------------------

        route, route_distance = (
            router.shortest_path(
                source_node,
                destination_node
            )
        )

        complete_route = [
            current_edge
        ] + route

        sumo_route = (
            RouteConverter.to_sumo_edge_ids(
                complete_route
            )
        )

        print(
            f"Calculated route distance: "
            f"{current_edge.distance + route_distance}"
        )

        print(
            f"Assigned route: {sumo_route}"
        )

        # --------------------------------------------------
        # Apply route
        # --------------------------------------------------

        traci.vehicle.setRoute(
            vehicle_id,
            sumo_route
        )

        # Read route immediately after assignment
        route_after_assignment = (
            list(
                traci.vehicle.getRoute(
                    vehicle_id
                )
            )
        )

        assert route_after_assignment == sumo_route

        print(
            "Route successfully assigned to SUMO."
        )

        # --------------------------------------------------
        # Advance SUMO
        # --------------------------------------------------

        for step in range(5):

            traci.simulationStep()

            # Vehicle may have completed its trip
            # during these steps.
            if vehicle_id not in traci.vehicle.getIDList():
                break

            current_route = list(
                traci.vehicle.getRoute(
                    vehicle_id
                )
            )

            route_index = traci.vehicle.getRouteIndex(
                vehicle_id
            )

            current_edge = traci.vehicle.getRoadID(
                vehicle_id
            )

            print(
                f"Step {step + 1}: "
                f"current_edge={current_edge}, "
                f"route_index={route_index}"
            )

            # The route should remain the route assigned
            # by Python while the vehicle is active.
            assert current_route == sumo_route

            assert 0 <= route_index < len(
                sumo_route
            )

        print(
            "\nSUMO route execution validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    test_route_execution()