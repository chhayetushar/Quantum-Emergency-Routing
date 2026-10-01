import traci

from Simulation.routing.road_graph import RoadGraph


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def test_road_graph():

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:

        graph = RoadGraph()

        graph.build_from_sumo()

        sumo_edge_ids = traci.edge.getIDList()

        routable_sumo_edges = {
            edge_id
            for edge_id in sumo_edge_ids
            if not edge_id.startswith(":")
        }

        expected_nodes = set()

        for edge_id in routable_sumo_edges:

            from_node = traci.edge.getFromJunction(
                edge_id
            )

            to_node = traci.edge.getToJunction(
                edge_id
            )

            if from_node and to_node:

                expected_nodes.add(
                    from_node
                )

                expected_nodes.add(
                    to_node
                )

        print(
            f"Total SUMO edges: "
            f"{len(sumo_edge_ids)}"
        )

        print(
            f"Routable SUMO edges: "
            f"{len(routable_sumo_edges)}"
        )

        print(
            f"Graph nodes: "
            f"{graph.node_count()}"
        )

        print(
            f"Expected graph nodes: "
            f"{len(expected_nodes)}"
        )

        print(
            f"Graph edges: "
            f"{graph.edge_count()}"
        )

        print(
            f"Node positions: "
            f"{len(graph.node_positions)}"
        )

        # --------------------------------------------------
        # Validate edges
        # --------------------------------------------------

        assert graph.edge_count() > 0

        assert set(graph.edges.keys()) == (
            routable_sumo_edges
        )

        # --------------------------------------------------
        # Validate nodes
        # --------------------------------------------------

        assert graph.nodes == expected_nodes

        assert graph.node_count() == len(
            expected_nodes
        )

        # --------------------------------------------------
        # Validate node positions
        # --------------------------------------------------

        assert set(
            graph.node_positions.keys()
        ) == graph.nodes

        for node_id in graph.nodes:

            position = graph.get_node_position(
                node_id
            )

            assert isinstance(
                position,
                tuple
            )

            assert len(position) == 2

            assert isinstance(
                position[0],
                (int, float)
            )

            assert isinstance(
                position[1],
                (int, float)
            )

        # --------------------------------------------------
        # Validate edges
        # --------------------------------------------------

        for edge_id, edge in graph.edges.items():

            assert edge.edge_id == edge_id

            assert edge.from_node in graph.nodes
            assert edge.to_node in graph.nodes

            assert edge.distance > 0
            assert edge.speed_limit >= 0

        # --------------------------------------------------
        # Validate adjacency
        # --------------------------------------------------

        for node_id, outgoing_edges in (
            graph.adjacency.items()
        ):

            assert node_id in graph.nodes

            for edge in outgoing_edges:

                assert edge.from_node == node_id
                assert edge.edge_id in graph.edges

        print(
            "Road graph coordinate validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    test_road_graph()