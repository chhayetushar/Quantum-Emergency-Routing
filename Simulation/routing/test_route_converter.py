from Simulation.routing.road_graph import GraphEdge
from Simulation.routing.route_converter import RouteConverter


def test_route_converter():

    route = [
        GraphEdge(
            edge_id="ROAD_A",
            from_node="NODE_1",
            to_node="NODE_2",
            distance=100.0,
            speed_limit=10.0
        ),
        GraphEdge(
            edge_id="ROAD_B",
            from_node="NODE_2",
            to_node="NODE_3",
            distance=150.0,
            speed_limit=10.0
        ),
        GraphEdge(
            edge_id="ROAD_C",
            from_node="NODE_3",
            to_node="NODE_4",
            distance=200.0,
            speed_limit=10.0
        )
    ]

    sumo_edge_ids = RouteConverter.to_sumo_edge_ids(
        route
    )

    print("GraphEdge route:")
    print(route)

    print("\nSUMO edge IDs:")
    print(sumo_edge_ids)

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    assert sumo_edge_ids == [
        "ROAD_A",
        "ROAD_B",
        "ROAD_C"
    ]

    # Order must remain unchanged
    assert sumo_edge_ids[0] == "ROAD_A"
    assert sumo_edge_ids[1] == "ROAD_B"
    assert sumo_edge_ids[2] == "ROAD_C"

    print(
        "\nRoute conversion validation successful!"
    )


if __name__ == "__main__":
    test_route_converter()