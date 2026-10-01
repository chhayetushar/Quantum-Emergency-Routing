import math
import time
import traci

from Simulation.routing.road_graph import RoadGraph
from Simulation.routing.dijkstra_router import DijkstraRouter
from Simulation.routing.a_star_router import AStarRouter


SUMO_BINARY = (
    r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"
)

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def find_test_nodes(
    graph: RoadGraph,
    hop_count: int = 20
) -> tuple[str, str]:
    """
    Find two connected graph nodes with a reasonable
    path length for comparing routing algorithms.
    """

    for edge in graph.edges.values():

        source_node = edge.from_node
        current_node = edge.to_node

        visited = {
            source_node
        }

        for _ in range(hop_count - 1):

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
            and current_node in graph.nodes
            and len(visited) >= 5
        ):
            return source_node, current_node

    raise ValueError(
        "Could not find suitable connected test nodes."
    )


def validate_route(
    route,
    source_node: str,
    destination_node: str
) -> None:
    """
    Validate that a route is connected from source
    to destination.
    """

    assert len(route) > 0

    assert route[0].from_node == source_node

    assert route[-1].to_node == destination_node

    for index in range(len(route) - 1):

        assert (
            route[index].to_node
            == route[index + 1].from_node
        )


def test_dijkstra_vs_a_star():

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

        print(
            f"Graph nodes: {graph.node_count()}"
        )

        print(
            f"Graph edges: {graph.edge_count()}"
        )

        # --------------------------------------------------
        # Select connected nodes
        # --------------------------------------------------

        source_node, destination_node = (
            find_test_nodes(
                graph
            )
        )

        print(
            f"Source node: {source_node}"
        )

        print(
            f"Destination node: {destination_node}"
        )

        # --------------------------------------------------
        # Create routers
        # --------------------------------------------------

        dijkstra_router = DijkstraRouter(
            graph
        )

        a_star_router = AStarRouter(
            graph
        )

        # --------------------------------------------------
        # Run Dijkstra
        # --------------------------------------------------

        start_time = time.perf_counter()

        dijkstra_route, dijkstra_distance = (
            dijkstra_router.shortest_path(
                source_node,
                destination_node
            )
        )

        dijkstra_time = (
            time.perf_counter()
            - start_time
        )

        # --------------------------------------------------
        # Run A*
        # --------------------------------------------------

        start_time = time.perf_counter()

        a_star_route, a_star_distance = (
            a_star_router.shortest_path(
                source_node,
                destination_node
            )
        )

        a_star_time = (
            time.perf_counter()
            - start_time
        )

        # --------------------------------------------------
        # Validate Dijkstra route
        # --------------------------------------------------

        validate_route(
            dijkstra_route,
            source_node,
            destination_node
        )

        calculated_dijkstra_distance = sum(
            edge.distance
            for edge in dijkstra_route
        )

        # --------------------------------------------------
        # Validate A* route
        # --------------------------------------------------

        validate_route(
            a_star_route,
            source_node,
            destination_node
        )

        calculated_a_star_distance = sum(
            edge.distance
            for edge in a_star_route
        )

        # --------------------------------------------------
        # Print values BEFORE assertions
        # --------------------------------------------------

        print("\nRouting Comparison")
        print("--------------------------------")

        print(
            f"Dijkstra edges: "
            f"{len(dijkstra_route)}"
        )

        print(
            f"Dijkstra returned distance: "
            f"{dijkstra_distance:.12f}"
        )

        print(
            f"Dijkstra calculated distance: "
            f"{calculated_dijkstra_distance:.12f}"
        )

        print(
            f"Dijkstra time: "
            f"{dijkstra_time:.6f} seconds"
        )

        print()

        print(
            f"A* edges: "
            f"{len(a_star_route)}"
        )

        print(
            f"A* returned distance: "
            f"{a_star_distance:.12f}"
        )

        print(
            f"A* calculated distance: "
            f"{calculated_a_star_distance:.12f}"
        )

        print(
            f"A* time: "
            f"{a_star_time:.6f} seconds"
        )

        print()

        print(
            f"Distance difference: "
            f"{abs(dijkstra_distance - a_star_distance):.12f}"
        )

        # --------------------------------------------------
        # Validate returned distance against route sum
        # --------------------------------------------------

        assert math.isclose(
            dijkstra_distance,
            calculated_dijkstra_distance,
            rel_tol=1e-9,
            abs_tol=1e-6
        )

        assert math.isclose(
            a_star_distance,
            calculated_a_star_distance,
            rel_tol=1e-9,
            abs_tol=1e-6
        )

        # --------------------------------------------------
        # Validate Dijkstra and A* objective
        # --------------------------------------------------

        assert math.isclose(
            dijkstra_distance,
            a_star_distance,
            rel_tol=1e-9,
            abs_tol=1e-6
        )

        print(
            "\nDijkstra and A* real-network "
            "distance validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    test_dijkstra_vs_a_star()