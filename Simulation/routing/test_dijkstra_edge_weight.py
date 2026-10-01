from Simulation.routing.road_graph import GraphEdge, RoadGraph
from Simulation.routing.dijkstra_router import DijkstraRouter


def test_dijkstra_edge_weight():

    graph = RoadGraph()

    # --------------------------------------------------
    # Route 1:
    #
    # A -> B -> D
    #
    # 5 + 5 = 10
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
            edge_id="B_D",
            from_node="B",
            to_node="D",
            distance=5.0,
            speed_limit=10.0
        )
    )

    # --------------------------------------------------
    # Route 2:
    #
    # A -> C -> D
    #
    # 3 + 10 = 13
    # --------------------------------------------------

    graph.add_edge(
        GraphEdge(
            edge_id="A_C",
            from_node="A",
            to_node="C",
            distance=3.0,
            speed_limit=10.0
        )
    )

    graph.add_edge(
        GraphEdge(
            edge_id="C_D",
            from_node="C",
            to_node="D",
            distance=10.0,
            speed_limit=10.0
        )
    )

    # --------------------------------------------------
    # Run Dijkstra
    # --------------------------------------------------

    router = DijkstraRouter(graph)

    route, total_distance = router.shortest_path(
        source_node="A",
        destination_node="D"
    )

    route_ids = [
        edge.edge_id
        for edge in route
    ]

    print("Selected route:")
    print(route_ids)

    print(
        f"Total distance: {total_distance}"
    )

    # --------------------------------------------------
    # Expected route
    # --------------------------------------------------

    assert route_ids == [
        "A_B",
        "B_D"
    ]

    assert total_distance == 10.0

    # --------------------------------------------------
    # Validate route connectivity
    # --------------------------------------------------

    assert route[0].from_node == "A"
    assert route[-1].to_node == "D"

    for index in range(len(route) - 1):

        assert (
            route[index].to_node
            == route[index + 1].from_node
        )

    print(
        "Dijkstra edge-weight validation successful!"
    )


if __name__ == "__main__":
    test_dijkstra_edge_weight()