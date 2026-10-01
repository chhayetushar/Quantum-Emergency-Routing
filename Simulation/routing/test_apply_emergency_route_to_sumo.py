import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.emergency_state import EmergencyState
from Simulation.state.emergency_vehicle_manager import (
    EmergencyVehicleManager
)

from Simulation.routing.road_graph import RoadGraph
from Simulation.routing.emergency_response_router import (
    EmergencyResponseRouter
)
from Simulation.routing.route_converter import RouteConverter


SUMO_BINARY = (
    r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"
)

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def find_emergency_destination(
    graph: RoadGraph,
    current_edge_id: str,
    hop_count: int = 5
) -> str:
    """
    Find a reachable destination edge starting from the
    emergency vehicle's current edge.

    The destination is selected from the real SUMO-derived
    RoadGraph, so the resulting route is based on actual
    network connectivity.
    """

    if current_edge_id not in graph.edges:
        raise ValueError(
            f"Current edge '{current_edge_id}' "
            f"is not present in RoadGraph."
        )

    current_edge = graph.edges[
        current_edge_id
    ]

    current_node = current_edge.to_node

    visited = {
        current_node
    }

    destination_edge_id = None

    for _ in range(hop_count):

        outgoing_edges = graph.get_neighbors(
            current_node
        )

        next_edge = None

        for candidate in outgoing_edges:

            if candidate.to_node not in visited:
                next_edge = candidate
                break

        if next_edge is None:
            break

        current_node = next_edge.to_node

        visited.add(
            current_node
        )

        destination_edge_id = (
            next_edge.edge_id
        )

    if destination_edge_id is None:
        raise ValueError(
            "Could not find a reachable emergency "
            "destination edge."
        )

    return destination_edge_id


def wait_for_emergency_vehicle(
    manager: EmergencyVehicleManager,
    simulation_state: SimulationState,
    max_steps: int = 100
):
    """
    Advance SUMO until an actual emergency vehicle is
    synchronized into SimulationState.

    We do NOT stop merely because an ordinary vehicle
    appears. This is important because the SUMO scenario
    may spawn normal vehicles before emergency vehicles.
    """

    for step in range(1, max_steps + 1):

        traci.simulationStep()

        emergency_vehicle_ids = (
            manager.synchronize_with_sumo()
        )

        if emergency_vehicle_ids:

            emergency_vehicle_id = (
                emergency_vehicle_ids[0]
            )

            print(
                f"Emergency vehicle found "
                f"at simulation step {step}: "
                f"{emergency_vehicle_id}"
            )

            if (
                emergency_vehicle_id
                not in simulation_state.emergency_vehicles
            ):

                raise RuntimeError(
                    f"Emergency vehicle "
                    f"'{emergency_vehicle_id}' "
                    "was synchronized but its state "
                    "is missing from SimulationState."
                )

            vehicle_state = (
                simulation_state
                .emergency_vehicles[
                    emergency_vehicle_id
                ]
            )

            return (
                emergency_vehicle_id,
                vehicle_state
            )

    # ------------------------------------------------------
    # Diagnostic output if no emergency vehicle appeared
    # ------------------------------------------------------

    print(
        "\nNo emergency vehicle was found "
        f"after {max_steps} simulation steps."
    )

    print(
        "\nActive SUMO vehicles:"
    )

    active_vehicle_ids = (
        traci.vehicle.getIDList()
    )

    for vehicle_id in active_vehicle_ids:

        vehicle_type = (
            traci.vehicle.getTypeID(
                vehicle_id
            )
        )

        current_edge = (
            traci.vehicle.getRoadID(
                vehicle_id
            )
        )

        print(
            f"  ID={vehicle_id}, "
            f"type={vehicle_type}, "
            f"edge={current_edge}"
        )

    raise RuntimeError(
        "No emergency vehicle appeared in SUMO "
        f"within {max_steps} simulation steps."
    )


def test_apply_emergency_route_to_sumo():

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:

        # ==================================================
        # 1. Create central SimulationState
        # ==================================================

        simulation_state = SimulationState()

        # ==================================================
        # 2. Create EmergencyVehicleManager using the same
        #    SimulationState
        # ==================================================

        emergency_vehicle_manager = (
            EmergencyVehicleManager(
                simulation_state
            )
        )

        # ==================================================
        # 3. Build real SUMO road graph
        # ==================================================

        graph = RoadGraph()

        graph.build_from_sumo()

        print(
            f"Graph nodes: "
            f"{graph.node_count()}"
        )

        print(
            f"Graph edges: "
            f"{graph.edge_count()}"
        )

        assert graph.node_count() > 0
        assert graph.edge_count() > 0

        # ==================================================
        # 4. Wait specifically for an emergency vehicle
        # ==================================================

        (
            emergency_vehicle_id,
            vehicle_state
        ) = wait_for_emergency_vehicle(
            manager=emergency_vehicle_manager,
            simulation_state=simulation_state,
            max_steps=100
        )

        # ==================================================
        # 5. Display synchronized emergency vehicle
        # ==================================================

        print(
            f"Emergency vehicle: "
            f"{emergency_vehicle_id}"
        )

        print(
            f"Vehicle type: "
            f"{vehicle_state.vehicle_type}"
        )

        print(
            f"Current edge: "
            f"{vehicle_state.current_edge}"
        )

        # ==================================================
        # 6. Validate current edge
        # ==================================================

        if not vehicle_state.current_edge:

            raise RuntimeError(
                "Emergency vehicle has no current edge."
            )

        current_edge_id = (
            vehicle_state.current_edge
        )

        if current_edge_id not in graph.edges:

            raise RuntimeError(
                f"Emergency vehicle current edge "
                f"'{current_edge_id}' is not present "
                f"in RoadGraph."
            )

        # ==================================================
        # 7. Select reachable emergency destination
        # ==================================================

        emergency_edge = (
            find_emergency_destination(
                graph,
                current_edge_id,
                hop_count=5
            )
        )

        print(
            f"Emergency edge: "
            f"{emergency_edge}"
        )

        assert emergency_edge in graph.edges

        # ==================================================
        # 8. Create EmergencyState
        # ==================================================

        emergency = EmergencyState(
            emergency_id="E001",
            emergency_type="MEDICAL",
            location=emergency_edge,
            severity="HIGH",
            creation_time=traci.simulation.getTime(),
            status="WAITING",
            assigned_vehicle=None
        )

        simulation_state.emergencies[
            "E001"
        ] = emergency

        # ==================================================
        # 9. Create EmergencyResponseRouter
        # ==================================================

        response_router = (
            EmergencyResponseRouter(
                simulation_state=simulation_state,
                graph=graph
            )
        )

        # ==================================================
        # 10. Plan emergency response route
        # ==================================================

        route, total_distance = (
            response_router.plan_route(
                vehicle_id=emergency_vehicle_id,
                emergency_id="E001"
            )
        )

        assert route
        assert len(route) > 0

        print(
            f"Emergency route edges: "
            f"{len(route)}"
        )

        print(
            f"Emergency route distance: "
            f"{total_distance:.2f}"
        )

        print(
            "\nEmergency route:"
        )

        for edge in route:

            print(
                edge.edge_id
            )

        # ==================================================
        # 11. Convert GraphEdge route to SUMO edge IDs
        # ==================================================

        sumo_route = (
            RouteConverter.to_sumo_edge_ids(
                route
            )
        )

        assert sumo_route
        assert len(sumo_route) == len(route)

        print(
            "\nSUMO route:"
        )

        for edge_id in sumo_route:

            print(
                edge_id
            )

        # ==================================================
        # 12. Verify all converted edges exist in SUMO
        # ==================================================

        sumo_edge_id_set = set(
            traci.edge.getIDList()
        )

        for edge_id in sumo_route:

            assert edge_id in sumo_edge_id_set, (
                f"Route edge '{edge_id}' "
                f"does not exist in SUMO."
            )

        # ==================================================
        # 13. Verify route starts at current edge
        # ==================================================

        assert (
            sumo_route[0]
            == current_edge_id
        ), (
            f"Emergency route starts at "
            f"'{sumo_route[0]}' but the emergency "
            f"vehicle is currently on "
            f"'{current_edge_id}'."
        )

        # ==================================================
        # 14. Apply route to real SUMO emergency vehicle
        # ==================================================

        traci.vehicle.setRoute(
            emergency_vehicle_id,
            sumo_route
        )

        print(
            "\nEmergency route assigned to SUMO "
            "vehicle successfully."
        )

        # ==================================================
        # 15. Read route back from SUMO
        # ==================================================

        applied_route = list(
            traci.vehicle.getRoute(
                emergency_vehicle_id
            )
        )

        assert (
            applied_route
            == sumo_route
        ), (
            "SUMO accepted a different route "
            "than the calculated emergency route."
            f"\nExpected: {sumo_route}"
            f"\nActual:   {applied_route}"
        )

        print(
            "\nApplied SUMO route:"
        )

        print(
            applied_route
        )

        # ==================================================
        # 16. Execute route for several simulation steps
        # ==================================================

        print(
            "\nEmergency route execution:"
        )

        for step in range(1, 6):

            traci.simulationStep()

            active_vehicle_ids = (
                traci.vehicle.getIDList()
            )

            if (
                emergency_vehicle_id
                not in active_vehicle_ids
            ):

                print(
                    f"Step {step}: "
                    "Emergency vehicle is no "
                    "longer active."
                )

                break

            current_sumo_edge = (
                traci.vehicle.getRoadID(
                    emergency_vehicle_id
                )
            )

            current_speed = (
                traci.vehicle.getSpeed(
                    emergency_vehicle_id
                )

            )

            print(
                f"Step {step}: "
                f"edge={current_sumo_edge}, "
                f"speed={current_speed:.2f}"
            )

        # ==================================================
        # 17. Verify route remains assigned
        # ==================================================

        if (
            emergency_vehicle_id
            in traci.vehicle.getIDList()
        ):

            final_route = list(
                traci.vehicle.getRoute(
                    emergency_vehicle_id
                )
            )

            assert (
                final_route
                == sumo_route
            ), (
                "Emergency route changed "
                "unexpectedly during execution."
            )

        # ==================================================
        # 18. Final validation
        # ==================================================

        print(
            "\nEmergency route application "
            "and execution validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    test_apply_emergency_route_to_sumo()