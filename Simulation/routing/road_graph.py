from dataclasses import dataclass, field

import traci


@dataclass(frozen=True)
class GraphEdge:
    """
    Represents one directed edge in the routing graph.
    """

    edge_id: str
    from_node: str
    to_node: str
    distance: float
    speed_limit: float


@dataclass
class RoadGraph:
    """
    Directed graph representation of the SUMO road network.
    """

    nodes: set[str] = field(
        default_factory=set
    )

    node_positions: dict[str, tuple[float, float]] = field(
        default_factory=dict
    )

    adjacency: dict[str, list[GraphEdge]] = field(
        default_factory=dict
    )

    edges: dict[str, GraphEdge] = field(
        default_factory=dict
    )

    def add_edge(
        self,
        edge: GraphEdge
    ) -> None:
        """
        Add a directed edge and both endpoint nodes.
        """

        self.edges[edge.edge_id] = edge

        self.nodes.add(
            edge.from_node
        )

        self.nodes.add(
            edge.to_node
        )

        self.adjacency.setdefault(
            edge.from_node,
            []
        ).append(edge)

    def add_node_position(
        self,
        node_id: str,
        position: tuple[float, float]
    ) -> None:
        """
        Store the SUMO coordinate of a graph node.
        """

        self.nodes.add(node_id)

        self.node_positions[node_id] = position

    def get_node_position(
        self,
        node_id: str
    ) -> tuple[float, float]:
        """
        Return the coordinate of a graph node.
        """

        if node_id not in self.node_positions:
            raise ValueError(
                f"No position is available for node '{node_id}'."
            )

        return self.node_positions[node_id]

    def get_neighbors(
        self,
        node_id: str
    ) -> list[GraphEdge]:
        """
        Return all outgoing edges from a node.
        """

        return self.adjacency.get(
            node_id,
            []
        )

    def build_from_sumo(self) -> None:
        """
        Build the complete routing graph from SUMO.

        Internal SUMO edges beginning with ':' are excluded.

        For every routable edge:
            - source junction is stored
            - destination junction is stored
            - junction coordinates are stored
            - first lane provides representative
              distance and speed-limit information
        """

        edge_ids = traci.edge.getIDList()

        for edge_id in edge_ids:

            # --------------------------------------------------
            # Ignore SUMO internal junction edges
            # --------------------------------------------------

            if edge_id.startswith(":"):
                continue

            # --------------------------------------------------
            # Get source and destination junctions
            # --------------------------------------------------

            from_node = traci.edge.getFromJunction(
                edge_id
            )

            to_node = traci.edge.getToJunction(
                edge_id
            )

            if not from_node or not to_node:
                continue

            # --------------------------------------------------
            # Get junction coordinates
            # --------------------------------------------------

            from_position = traci.junction.getPosition(
                from_node
            )

            to_position = traci.junction.getPosition(
                to_node
            )

            self.add_node_position(
                from_node,
                from_position
            )

            self.add_node_position(
                to_node,
                to_position
            )

            # --------------------------------------------------
            # Get number of lanes
            # --------------------------------------------------

            lane_count = traci.edge.getLaneNumber(
                edge_id
            )

            if lane_count <= 0:
                continue

            # --------------------------------------------------
            # Use first lane as representative lane
            # --------------------------------------------------

            first_lane_id = f"{edge_id}_0"

            distance = traci.lane.getLength(
                first_lane_id
            )

            speed_limit = traci.lane.getMaxSpeed(
                first_lane_id
            )

            # --------------------------------------------------
            # Validate distance
            # --------------------------------------------------

            if distance <= 0:
                continue

            # --------------------------------------------------
            # Create graph edge
            # --------------------------------------------------

            graph_edge = GraphEdge(
                edge_id=edge_id,
                from_node=from_node,
                to_node=to_node,
                distance=distance,
                speed_limit=speed_limit
            )

            # --------------------------------------------------
            # Add graph edge
            # --------------------------------------------------

            self.add_edge(
                graph_edge
            )

    def node_count(self) -> int:
        """
        Return the total number of unique graph nodes.
        """

        return len(
            self.nodes
        )

    def edge_count(self) -> int:
        """
        Return the number of graph edges.
        """

        return len(
            self.edges
        )