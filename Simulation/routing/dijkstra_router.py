import heapq

from Simulation.routing.road_graph import RoadGraph, GraphEdge


class DijkstraRouter:
    """
    Calculates shortest paths on a RoadGraph
    using Dijkstra's algorithm.

    Initial routing cost:
        edge distance
    """

    def __init__(self, graph: RoadGraph):
        self.graph = graph

    def shortest_path(
        self,
        source_node: str,
        destination_node: str
    ) -> tuple[list[GraphEdge], float]:
        """
        Calculate the shortest path between two nodes.

        Returns:
            (
                ordered list of GraphEdge objects,
                total distance
            )
        """

        # --------------------------------------------------
        # Validate source
        # --------------------------------------------------

        if source_node not in self.graph.nodes:
            raise ValueError(
                f"Source node '{source_node}' does not exist."
            )

        # --------------------------------------------------
        # Validate destination
        # --------------------------------------------------

        if destination_node not in self.graph.nodes:
            raise ValueError(
                f"Destination node '{destination_node}' "
                f"does not exist."
            )

        # --------------------------------------------------
        # Special case: source == destination
        # --------------------------------------------------

        if source_node == destination_node:
            return [], 0.0

        # --------------------------------------------------
        # Initial distances
        # --------------------------------------------------

        distances = {
            source_node: 0.0
        }

        # --------------------------------------------------
        # Previous-node / previous-edge information
        # --------------------------------------------------

        previous = {}

        # --------------------------------------------------
        # Priority queue
        #
        # (current_distance, node_id)
        # --------------------------------------------------

        priority_queue = [
            (0.0, source_node)
        ]

        # --------------------------------------------------
        # Dijkstra search
        # --------------------------------------------------

        while priority_queue:

            current_distance, current_node = (
                heapq.heappop(priority_queue)
            )

            # Ignore stale queue entries
            if current_distance > distances.get(
                current_node,
                float("inf")
            ):
                continue

            # Destination reached
            if current_node == destination_node:
                break

            # --------------------------------------------------
            # Examine outgoing edges
            # --------------------------------------------------

            for edge in self.graph.get_neighbors(
                current_node
            ):

                new_distance = (
                    current_distance
                    + edge.distance
                )

                known_distance = distances.get(
                    edge.to_node,
                    float("inf")
                )

                # --------------------------------------------------
                # Found a cheaper route
                # --------------------------------------------------

                if new_distance < known_distance:

                    distances[
                        edge.to_node
                    ] = new_distance

                    previous[
                        edge.to_node
                    ] = (
                        current_node,
                        edge
                    )

                    heapq.heappush(
                        priority_queue,
                        (
                            new_distance,
                            edge.to_node
                        )
                    )

        # --------------------------------------------------
        # Destination unreachable
        # --------------------------------------------------

        if destination_node not in distances:
            raise ValueError(
                f"No route exists from "
                f"'{source_node}' to "
                f"'{destination_node}'."
            )

        # --------------------------------------------------
        # Reconstruct route
        # --------------------------------------------------

        route = []

        current_node = destination_node

        while current_node != source_node:

            previous_node, edge = previous[
                current_node
            ]

            route.append(edge)

            current_node = previous_node

        route.reverse()

        total_distance = distances[
            destination_node
        ]

        return route, total_distance