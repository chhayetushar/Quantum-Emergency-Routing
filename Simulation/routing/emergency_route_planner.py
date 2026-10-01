from Simulation.routing.road_graph import RoadGraph, GraphEdge
from Simulation.routing.dijkstra_router import DijkstraRouter


class EmergencyRoutePlanner:
    """
    Builds a route from an emergency vehicle's current
    road edge to the road containing an emergency.
    """

    def __init__(self, graph: RoadGraph):
        self.graph = graph
        self.router = DijkstraRouter(graph)

    def plan_route(
        self,
        vehicle_edge_id: str,
        emergency_edge_id: str
    ) -> tuple[list[GraphEdge], float]:
        """
        Calculate a route from the vehicle's current edge
        to the emergency edge.

        The emergency edge is included as the final edge.
        """

        # --------------------------------------------------
        # Validate vehicle edge
        # --------------------------------------------------

        if vehicle_edge_id not in self.graph.edges:
            raise ValueError(
                f"Vehicle edge '{vehicle_edge_id}' "
                f"does not exist in the road graph."
            )

        # --------------------------------------------------
        # Validate emergency edge
        # --------------------------------------------------

        if emergency_edge_id not in self.graph.edges:
            raise ValueError(
                f"Emergency edge '{emergency_edge_id}' "
                f"does not exist in the road graph."
            )

        vehicle_edge = self.graph.edges[
            vehicle_edge_id
        ]

        emergency_edge = self.graph.edges[
            emergency_edge_id
        ]

        # --------------------------------------------------
        # Vehicle is already on emergency edge
        # --------------------------------------------------

        if vehicle_edge_id == emergency_edge_id:
            return (
                [vehicle_edge],
                vehicle_edge.distance
            )

        # --------------------------------------------------
        # Routing source
        #
        # Start from the end of the vehicle's
        # current edge.
        # --------------------------------------------------

        source_node = vehicle_edge.to_node

        # --------------------------------------------------
        # Routing destination
        #
        # Reach the beginning of the emergency edge.
        # --------------------------------------------------

        destination_node = emergency_edge.from_node

        # --------------------------------------------------
        # Calculate route to emergency edge
        # --------------------------------------------------

        route_to_emergency, route_distance = (
            self.router.shortest_path(
                source_node,
                destination_node
            )
        )

        # --------------------------------------------------
        # Append emergency edge
        # --------------------------------------------------

        complete_route = (
            [vehicle_edge]
            + route_to_emergency
            + [emergency_edge]
        )

        total_distance = (
            vehicle_edge.distance
            + route_distance
            + emergency_edge.distance
        )

        return (
            complete_route,
            total_distance
        )