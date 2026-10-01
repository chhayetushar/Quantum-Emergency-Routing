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


def find_test_nodes(
    graph: RoadGraph
) -> tuple[str, str]:
    """
    Find two connected nodes for routing validation.
    """

    for edge in graph.edges.values():

        source_node = edge.from_node
        current_node = edge.to_node

        visited = {
            source_node
        }

        for _ in range(15):

            if current_node in visited:
                break

            visited.add(
                current_node
            )

            outgoing_edges = graph.get_neighbors(
                current_node
            )

            if not outgoing_edges:
                break

            next_edge = None

            for candidate in outgoing_edges:

                if candidate.to_node not in visited:
                    next_edge = candidate
                    break

            if next_edge is None:
                break

            current_node = next_edge.to_node

        if (
            current_node != source_node
            and len(visited) >= 5
        ):
            return (
                source_node,
                current_node
            )

    raise ValueError(
        "Could not find connected test nodes."
    )


def test_real_route_conversion():

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
        # Find connected source and destination
        # --------------------------------------------------

        source_node, destination_node = (
            find_test_nodes(graph)
        )

        print(
            f"Source node: "
            f"{source_node}"
        )

        print(
            f"Destination node: "
            f"{destination_node}"
        )

        # --------------------------------------------------
        # Run Dijkstra
        # --------------------------------------------------

        router = DijkstraRouter(
            graph
        )

        route, total_distance = (
            router.shortest_path(
                source_node,
                destination_node
            )
        )

        # --------------------------------------------------
        # Convert route to SUMO edge IDs
        # --------------------------------------------------

        sumo_edge_ids = (
            RouteConverter.to_sumo_edge_ids(
                route
            )
        )

        print(
            f"GraphEdge count: "
            f"{len(route)}"
        )

        print(
            f"SUMO edge ID count: "
            f"{len(sumo_edge_ids)}"
        )

        print(
            f"Total distance: "
            f"{total_distance}"
        )

        print("\nSUMO route edge IDs:")

        for edge_id in sumo_edge_ids:

            print(
                edge_id
            )

        # --------------------------------------------------
        # Get actual SUMO edge IDs
        # --------------------------------------------------

        sumo_edge_id_set = set(
            traci.edge.getIDList()
        )

        # --------------------------------------------------
        # Validate route conversion
        # --------------------------------------------------

        assert len(sumo_edge_ids) == len(route)

        assert len(sumo_edge_ids) > 0

        # Every converted ID must exist in SUMO
        for edge_id in sumo_edge_ids:

            assert edge_id in sumo_edge_id_set

        # --------------------------------------------------
        # Validate route order
        # --------------------------------------------------

        for index, edge_id in enumerate(
            sumo_edge_ids
        ):

            assert (
                edge_id
                == route[index].edge_id
            )

        # --------------------------------------------------
        # Validate connectivity
        # --------------------------------------------------

        for index in range(
            len(route) - 1
        ):

            assert (
                route[index].to_node
                == route[index + 1].from_node
            )

        print(
            "\nReal SUMO route conversion "
            "validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    test_real_route_conversion()