import heapq
import math

from Simulation.routing.road_graph import RoadGraph, GraphEdge


class AStarRouter:
    """
    Calculates shortest paths on a RoadGraph
    using the A* algorithm.

    Initial routing cost:
        edge distance

    Heuristic:
        Safely scaled straight-line distance.
    """

    def __init__(self, graph: RoadGraph):
        self.graph = graph

        self.heuristic_scale = (
            self._calculate_heuristic_scale()
        )

    def _calculate_heuristic_scale(self) -> float:
        """
        Calculate a globally safe scaling factor for the
        straight-line heuristic.

        For every edge:

            edge distance
            ------------------------
            straight-line node distance

        The minimum ratio is used as the global scale.

        This prevents the heuristic from overestimating
        the remaining graph cost.
        """

        minimum_ratio = 1.0

        found_valid_ratio = False

        for edge in self.graph.edges.values():

            if (
                edge.from_node
                not in self.graph.node_positions
            ):
                continue

            if (
                edge.to_node
                not in self.graph.node_positions
            ):
                continue

            x1, y1 = self.graph.node_positions[
                edge.from_node
            ]

            x2, y2 = self.graph.node_positions[
                edge.to_node
            ]

            straight_line_distance = math.hypot(
                x2 - x1,
                y2 - y1
            )

            # If both junction coordinates are identical,
            # they provide no useful heuristic information.
            if straight_line_distance <= 0:
                continue

            ratio = (
                edge.distance
                / straight_line_distance
            )

            minimum_ratio = min(
                minimum_ratio,
                ratio
            )

            found_valid_ratio = True

        if not found_valid_ratio:
            return 0.0

        # Never make the heuristic larger than raw
        # Euclidean distance.
        return min(
            1.0,
            minimum_ratio
        )

    def heuristic(
        self,
        node_id: str,
        destination_node: str
    ) -> float:
        """
        Return a safe lower-bound estimate of the
        remaining distance.
        """

        x1, y1 = self.graph.get_node_position(
            node_id
        )

        x2, y2 = self.graph.get_node_position(
            destination_node
        )

        straight_line_distance = math.hypot(
            x2 - x1,
            y2 - y1
        )

        return (
            self.heuristic_scale
            * straight_line_distance
        )

    def shortest_path(
        self,
        source_node: str,
        destination_node: str
    ) -> tuple[list[GraphEdge], float]:
        """
        Calculate the shortest path between two nodes
        using A*.

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
        # Source == destination
        # --------------------------------------------------

        if source_node == destination_node:
            return [], 0.0

        # --------------------------------------------------
        # Actual distance from source
        # --------------------------------------------------

        distances = {
            source_node: 0.0
        }

        # --------------------------------------------------
        # Previous node and edge
        # --------------------------------------------------

        previous = {}

        # --------------------------------------------------
        # Priority queue
        #
        # (f_score, g_score, node_id)
        # --------------------------------------------------

        initial_heuristic = self.heuristic(
            source_node,
            destination_node
        )

        priority_queue = [
            (
                initial_heuristic,
                0.0,
                source_node
            )
        ]

        # --------------------------------------------------
        # A* search
        # --------------------------------------------------

        while priority_queue:

            (
                current_f,
                current_distance,
                current_node
            ) = heapq.heappop(
                priority_queue
            )

            # --------------------------------------------------
            # Ignore stale queue entry
            # --------------------------------------------------

            if current_distance > distances.get(
                current_node,
                float("inf")
            ):
                continue

            # --------------------------------------------------
            # Destination reached
            # --------------------------------------------------

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
                # Found a cheaper path
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

                    estimated_remaining = (
                        self.heuristic(
                            edge.to_node,
                            destination_node
                        )
                    )

                    f_score = (
                        new_distance
                        + estimated_remaining
                    )

                    heapq.heappush(
                        priority_queue,
                        (
                            f_score,
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