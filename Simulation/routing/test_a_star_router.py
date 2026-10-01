from Simulation.routing.road_graph import GraphEdge, RoadGraph
from Simulation.routing.a_star_router import AStarRouter


def test_a_star_router():

    graph = RoadGraph()

    # --------------------------------------------------
    # Define node coordinates
    # --------------------------------------------------

    graph.add_node_position(
        "A",
        (0.0, 0.0)
    )

    graph.add_node_position(
        "B",
        (1.0, 0.0)
    )

    graph.add_node_position(
        "C",
        (0.0, 2.0)
    )

    graph.add_node_position(
        "D",
        (2.0, 0.0)
    )

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
    # 6 + 8 = 14
    # --------------------------------------------------

    graph.add_edge(
        GraphEdge(
            edge_id="A_C",
            from_node="A",
            to_node="C",
            distance=6.0,
            speed_limit=10.0
        )
    )

    graph.add_edge(
        GraphEdge(
            edge_id="C_D",
            from_node="C",
            to_node="D",
            distance=8.0,
            speed_limit=10.0
        )
    )

    router = AStarRouter(
        graph
    )

    route, total_distance = router.shortest_path(
        source_node="A",
        destination_node="D"
    )

    route_ids = [
        edge.edge_id
        for edge in route
    ]

    print("Selected A* route:")
    print(route_ids)

    print(
        f"Total distance: {total_distance}"
    )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    assert route_ids == [
        "A_B",
        "B_D"
    ]

    assert total_distance == 10.0

    assert route[0].from_node == "A"

    assert route[-1].to_node == "D"

    print(
        "A* routing validation successful!"
    )


if __name__ == "__main__":
    test_a_star_router()