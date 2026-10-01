from Simulation.routing.road_graph import GraphEdge, RoadGraph
from Simulation.routing.dijkstra_router import DijkstraRouter


def test_dijkstra_edge_cases():

    graph = RoadGraph()

    # --------------------------------------------------
    # Connected component
    #
    # A -> B -> C
    # --------------------------------------------------

    graph.add_edge(
        GraphEdge(
            edge_id="A_B",
            from_node="A",
            to_node="B",
            distance=5.0,
            speed_limit=10.0
        )
    )

    graph.add_edge(
        GraphEdge(
            edge_id="B_C",
            from_node="B",
            to_node="C",
            distance=7.0,
            speed_limit=10.0
        )
    )

    # --------------------------------------------------
    # Separate disconnected component
    #
    # X -> Y
    # --------------------------------------------------

    graph.add_edge(
        GraphEdge(
            edge_id="X_Y",
            from_node="X",
            to_node="Y",
            distance=3.0,
            speed_limit=10.0
        )
    )

    router = DijkstraRouter(graph)

    # --------------------------------------------------
    # Test 1: Source equals destination
    # --------------------------------------------------

    route, total_distance = router.shortest_path(
        source_node="A",
        destination_node="A"
    )

    assert route == []
    assert total_distance == 0.0

    print("Source-equals-destination case passed.")

    # --------------------------------------------------
    # Test 2: Invalid source
    # --------------------------------------------------

    try:

        router.shortest_path(
            source_node="INVALID",
            destination_node="A"
        )

        raise AssertionError(
            "Invalid source node was accepted."
        )

    except ValueError as error:

        assert "Source node" in str(error)

    print("Invalid-source case passed.")

    # --------------------------------------------------
    # Test 3: Invalid destination
    # --------------------------------------------------

    try:

        router.shortest_path(
            source_node="A",
            destination_node="INVALID"
        )

        raise AssertionError(
            "Invalid destination node was accepted."
        )

    except ValueError as error:

        assert "Destination node" in str(error)

    print("Invalid-destination case passed.")

    # --------------------------------------------------
    # Test 4: No route exists
    # --------------------------------------------------

    try:

        router.shortest_path(
            source_node="A",
            destination_node="Y"
        )

        raise AssertionError(
            "Disconnected nodes produced a route."
        )

    except ValueError as error:

        assert "No route exists" in str(error)

    print("Disconnected-route case passed.")

    # --------------------------------------------------
    # Final validation
    # --------------------------------------------------

    print(
        "Dijkstra edge-case validation successful!"
    )


if __name__ == "__main__":
    test_dijkstra_edge_cases()