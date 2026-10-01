import traci

from Simulation.routing.road_graph import RoadGraph
from Simulation.routing.dijkstra_router import DijkstraRouter


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def find_connected_test_nodes(
    graph: RoadGraph
) -> tuple[str, str]:

    for first_edge in graph.edges.values():

        source_node = first_edge.from_node
        intermediate_node = first_edge.to_node

        outgoing_edges = graph.get_neighbors(
            intermediate_node
        )

        if outgoing_edges:

            destination_node = (
                outgoing_edges[0].to_node
            )

            if destination_node != source_node:

                return (
                    source_node,
                    destination_node
                )

    raise ValueError(
        "Could not find connected test nodes."
    )


def test_dijkstra_router():

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:

        # --------------------------------------------------
        # Build graph
        # --------------------------------------------------

        graph = RoadGraph()

        graph.build_from_sumo()

        # --------------------------------------------------
        # Find guaranteed connected test nodes
        # --------------------------------------------------

        source_node, destination_node = (
            find_connected_test_nodes(graph)
        )

        print(
            f"Source node: {source_node}"
        )

        print(
            f"Destination node: {destination_node}"
        )

        # --------------------------------------------------
        # Create router
        # --------------------------------------------------

        router = DijkstraRouter(
            graph
        )

        # --------------------------------------------------
        # Calculate route
        # --------------------------------------------------

        route, total_distance = (
            router.shortest_path(
                source_node,
                destination_node
            )
        )

        print(
            f"Route edges: {len(route)}"
        )

        print(
            f"Total distance: "
            f"{total_distance}"
        )

        print("\nRoute:")

        for edge in route:

            print(
                f"{edge.edge_id}: "
                f"{edge.from_node} -> "
                f"{edge.to_node}, "
                f"distance={edge.distance}"
            )

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        assert len(route) > 0

        assert route[0].from_node == source_node

        assert route[-1].to_node == destination_node

        calculated_distance = sum(
            edge.distance
            for edge in route
        )

        assert (
            abs(
                calculated_distance
                - total_distance
            )
            < 1e-9
        )

        for index in range(
            len(route) - 1
        ):

            assert (
                route[index].to_node
                == route[index + 1].from_node
            )

        print(
            "\nDijkstra routing validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    test_dijkstra_router()