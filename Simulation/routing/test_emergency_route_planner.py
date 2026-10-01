from Simulation.routing.road_graph import GraphEdge, RoadGraph
from Simulation.routing.emergency_route_planner import EmergencyRoutePlanner


def test_emergency_route_planner():

    graph = RoadGraph()

    # --------------------------------------------------
    # Graph:
    #
    # A → B → C → D
    #          \
    #           → E
    # --------------------------------------------------

    graph.add_edge(
        GraphEdge(
            edge_id="A_B",
            from_node="A",
            to_node="B",
            distance=10.0,
            speed_limit=10.0
        )
    )

    graph.add_edge(
        GraphEdge(
            edge_id="B_C",
            from_node="B",
            to_node="C",
            distance=20.0,
            speed_limit=10.0
        )
    )

    graph.add_edge(
        GraphEdge(
            edge_id="C_D",
            from_node="C",
            to_node="D",
            distance=30.0,
            speed_limit=10.0
        )
    )

    graph.add_edge(
        GraphEdge(
            edge_id="C_E",
            from_node="C",
            to_node="E",
            distance=5.0,
            speed_limit=10.0
        )
    )

    # --------------------------------------------------
    # Vehicle starts on A_B
    # Emergency is on C_E
    # --------------------------------------------------

    planner = EmergencyRoutePlanner(
        graph
    )

    route, total_distance = planner.plan_route(
        vehicle_edge_id="A_B",
        emergency_edge_id="C_E"
    )

    route_ids = [
        edge.edge_id
        for edge in route
    ]

    print("Emergency route:")
    print(route_ids)

    print(
        f"Total distance: "
        f"{total_distance}"
    )

    # --------------------------------------------------
    # Expected:
    #
    # A_B → B_C → C_E
    #
    # 10 + 20 + 5 = 35
    # --------------------------------------------------

    assert route_ids == [
        "A_B",
        "B_C",
        "C_E"
    ]

    assert total_distance == 35.0

    # --------------------------------------------------
    # Validate route connectivity
    # --------------------------------------------------

    assert route[0].from_node == "A"

    assert route[-1].to_node == "E"

    for index in range(
        len(route) - 1
    ):

        assert (
            route[index].to_node
            == route[index + 1].from_node
        )

    print(
        "Emergency route planner validation successful!"
    )


if __name__ == "__main__":
    test_emergency_route_planner()