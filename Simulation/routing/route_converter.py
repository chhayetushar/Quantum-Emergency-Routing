from Simulation.routing.road_graph import GraphEdge


class RouteConverter:
    """
    Converts routing results into SUMO-compatible
    edge ID sequences.
    """

    @staticmethod
    def to_sumo_edge_ids(
        route: list[GraphEdge]
    ) -> list[str]:
        """
        Convert an ordered GraphEdge route into
        an ordered list of SUMO edge IDs.
        """

        return [
            edge.edge_id
            for edge in route
        ]