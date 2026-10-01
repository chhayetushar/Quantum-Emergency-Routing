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
    Build a connected destination starting from the
    current edge and calculate a Dijkstra route toward it.
    """

    if current_edge_id not in graph.edges:
        raise ValueError(
            f"Current edge '{current_edge_id}' "
            f"is not present in RoadGraph."
        )

    current_edge = graph.edges[
        current_edge_id
    ]

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

    return (
        current_edge,
        source_node,
        destination_node
    )


def test_apply_route_to_sumo():

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
        # Find a real active vehicle
        # --------------------------------------------------

        vehicle_id = None
        current_edge_id = None

        for _ in range(10):

            traci.simulationStep()

            active_vehicle_ids = (
                traci.vehicle.getIDList()
            )

            for candidate_vehicle_id in (
                active_vehicle_ids
            ):

                candidate_edge_id = (
                    traci.vehicle.getRoadID(
                        candidate_vehicle_id
                    )
                )

                # Ignore SUMO internal edges
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
            f"Current edge: {current_edge_id}"
        )

        # --------------------------------------------------
        # Find a connected destination
        # --------------------------------------------------

        (
            current_edge,
            source_node,
            destination_node
        ) = find_test_route(
            graph,
            current_edge_id
        )

        print(
            f"Routing source node: {source_node}"
        )

        print(
            f"Destination node: {destination_node}"
        )

        # --------------------------------------------------
        # Calculate suffix route with Dijkstra
        # --------------------------------------------------

        suffix_route, suffix_distance = (
            router.shortest_path(
                source_node,
                destination_node
            )
        )

        # --------------------------------------------------
        # Include the vehicle's current edge
        # --------------------------------------------------

        complete_route = [
            current_edge
        ] + suffix_route

        # --------------------------------------------------
        # Convert to SUMO edge IDs
        # --------------------------------------------------

        sumo_route = (
            RouteConverter.to_sumo_edge_ids(
                complete_route
            )
        )

        print(
            f"Calculated route edges: "
            f"{len(complete_route)}"
        )

        print(
            f"Calculated route distance: "
            f"{current_edge.distance + suffix_distance}"
        )

        print("\nCalculated SUMO route:")

        for edge_id in sumo_route:

            print(
                edge_id
            )

        # --------------------------------------------------
        # Apply route to real SUMO vehicle
        # --------------------------------------------------

        traci.vehicle.setRoute(
            vehicle_id,
            sumo_route
        )

        # --------------------------------------------------
        # Verify SUMO accepted the route
        # --------------------------------------------------

        applied_route = traci.vehicle.getRoute(
            vehicle_id
        )

        assert applied_route == tuple(
            sumo_route
        ) or list(applied_route) == sumo_route

        print(
            "\nRoute applied to SUMO vehicle:"
        )

        print(
            applied_route
        )

        print(
            "\nSUMO route application validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    test_apply_route_to_sumo()