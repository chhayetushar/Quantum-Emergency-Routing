import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.emergency_vehicle_manager import EmergencyVehicleManager
from Simulation.state.emergency_state import EmergencyState

from Simulation.routing.road_graph import RoadGraph
from Simulation.routing.emergency_response_router import EmergencyResponseRouter
from Simulation.routing.route_converter import RouteConverter


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"
SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def find_emergency_vehicle(manager, simulation_state):
    """
    Run SUMO until an emergency vehicle appears.
    """

    for step in range(100):

        traci.simulationStep()

        emergency_ids = manager.synchronize_with_sumo()

        if emergency_ids:

            vehicle_id = emergency_ids[0]

            vehicle = simulation_state.emergency_vehicles[
                vehicle_id
            ]

            print(
                f"Emergency vehicle found at simulation step "
                f"{step + 1}: {vehicle_id}"
            )

            return vehicle_id

    raise RuntimeError(
        "No emergency vehicle appeared in SUMO."
    )


def find_short_route(
    router,
    simulation_state,
    vehicle_id,
    emergency_id,
    graph
):
    """
    Find a reachable destination with a reasonably short route.
    """

    vehicle = simulation_state.emergency_vehicles[
        vehicle_id
    ]

    candidate_edges = list(graph.edges.keys())

    for candidate_edge in candidate_edges:

        if candidate_edge == vehicle.current_edge:
            continue

        emergency = EmergencyState(
            emergency_id=emergency_id,
            emergency_type="TRAFFIC_ACCIDENT",
            location=candidate_edge,
            severity="HIGH",
            creation_time=0.0
        )

        simulation_state.emergencies[
            emergency_id
        ] = emergency

        try:

            route, distance = router.plan_route(
                vehicle_id=vehicle_id,
                emergency_id=emergency_id
            )

            if route and len(route) <= 20:
                return emergency, route, distance

        except Exception:
            pass

        simulation_state.emergencies.pop(
            emergency_id,
            None
        )

    raise RuntimeError(
        "Could not find a suitable reachable emergency destination."
    )


def apply_route(vehicle_id, route):
    """
    Convert a GraphEdge route to SUMO edge IDs and apply it.

    SUMO may normalize the route after setRoute(), so validation
    checks route usability rather than requiring byte-for-byte
    equality with the requested route.
    """

    sumo_route = RouteConverter.to_sumo_edge_ids(
        route
    )

    if not sumo_route:
        raise AssertionError(
            "Converted SUMO route is empty."
        )

    current_edge = traci.vehicle.getRoadID(
        vehicle_id
    )

    # The first edge returned by the graph route should normally
    # correspond to the vehicle's current edge. Internal SUMO
    # junction edges are allowed during execution.
    if (
        current_edge not in sumo_route
        and not current_edge.startswith(":")
    ):
        raise AssertionError(
            "Current SUMO edge is not present in the requested "
            "route.\n"
            f"Current edge: {current_edge}\n"
            f"Requested first edge: {sumo_route[0]}"
        )

    traci.vehicle.setRoute(
        vehicle_id,
        sumo_route
    )

    applied_route = list(
        traci.vehicle.getRoute(vehicle_id)
    )

    if not applied_route:
        raise AssertionError(
            "SUMO returned an empty route after setRoute()."
        )

    # The route must still contain the requested destination.
    requested_destination = sumo_route[-1]

    if requested_destination not in applied_route:
        raise AssertionError(
            "SUMO route does not contain the requested "
            "destination.\n"
            f"Requested destination: "
            f"{requested_destination}\n"
            f"Applied route: {applied_route}"
        )

    return applied_route


def main():

    simulation_state = SimulationState()

    manager = EmergencyVehicleManager(
        simulation_state
    )

    graph = RoadGraph()

    traci.start(
        [
            SUMO_BINARY,
            "-c",
            SUMO_CONFIG,
            "--start",
            "--quit-on-end",
        ]
    )

    try:

        # =========================================================
        # 1. Build graph
        # =========================================================

        graph.build_from_sumo()

        print(f"Graph nodes: {graph.node_count()}")
        print(f"Graph edges: {graph.edge_count()}")

        # =========================================================
        # 2. Find emergency vehicle
        # =========================================================

        vehicle_id = find_emergency_vehicle(
            manager,
            simulation_state
        )

        vehicle = simulation_state.emergency_vehicles[
            vehicle_id
        ]

        original_edge = vehicle.current_edge

        print()
        print(f"Emergency vehicle: {vehicle_id}")
        print(f"Vehicle type: {vehicle.vehicle_type}")
        print(f"Original edge: {original_edge}")
        print(f"Initial status: {vehicle.status}")

        if vehicle.status != "AVAILABLE":
            raise AssertionError(
                f"Expected AVAILABLE, got {vehicle.status}"
            )

        # =========================================================
        # 3. Create emergency and assign vehicle
        # =========================================================

        response_router = EmergencyResponseRouter(
            simulation_state=simulation_state,
            graph=graph
        )

        emergency, emergency_route, emergency_distance = (
            find_short_route(
                router=response_router,
                simulation_state=simulation_state,
                vehicle_id=vehicle_id,
                emergency_id="E_COMPLETE_001",
                graph=graph
            )
        )

        manager.assign_emergency(
            vehicle_id=vehicle_id,
            emergency_id=emergency.emergency_id
        )

        manager.update_status(
            vehicle_id=vehicle_id,
            new_status="ASSIGNED"
        )

        vehicle = simulation_state.emergency_vehicles[
            vehicle_id
        ]

        if vehicle.status != "ASSIGNED":
            raise AssertionError(
                "Vehicle did not enter ASSIGNED state."
            )

        print()
        print("Emergency assigned.")
        print(
            f"Emergency edge: {emergency.location}"
        )
        print(
            f"Emergency route edges: "
            f"{len(emergency_route)}"
        )
        print(
            f"Emergency route distance: "
            f"{emergency_distance:.2f}"
        )

        # =========================================================
        # 4. Apply emergency route
        # =========================================================

        apply_route(
            vehicle_id,
            emergency_route
        )

        manager.update_status(
            vehicle_id=vehicle_id,
            new_status="EN_ROUTE"
        )

        print(
            f"Vehicle status: {vehicle.status}"
        )

        # =========================================================
        # 5. Travel to emergency scene
        # =========================================================

        scene_reached = False

        print()
        print("Travelling to emergency scene:")

        for step in range(100):

            traci.simulationStep()

            manager.synchronize_with_sumo()

            vehicle = simulation_state.emergency_vehicles[
                vehicle_id
            ]

            print(
                f"Scene step {step + 1}: "
                f"edge={vehicle.current_edge}, "
                f"speed={vehicle.speed:.2f}, "
                f"position={vehicle.position:.2f}, "
                f"status={vehicle.status}"
            )

            if (
                vehicle.status == "EN_ROUTE"
                and vehicle.current_edge
                == emergency.location
            ):

                manager.update_status(
                    vehicle_id=vehicle_id,
                    new_status="AT_SCENE"
                )

                scene_reached = True

                break

        if not scene_reached:
            raise AssertionError(
                "Vehicle did not reach the emergency scene."
            )

        vehicle = simulation_state.emergency_vehicles[
            vehicle_id
        ]

        if vehicle.status != "AT_SCENE":
            raise AssertionError(
                f"Expected AT_SCENE, got {vehicle.status}"
            )

        print()
        print("Emergency scene reached.")
        print(
            f"Vehicle status: {vehicle.status}"
        )

        # =========================================================
        # 6. Begin return lifecycle
        # =========================================================

        manager.update_status(
            vehicle_id=vehicle_id,
            new_status="RETURNING"
        )

        vehicle = simulation_state.emergency_vehicles[
            vehicle_id
        ]

        if vehicle.status != "RETURNING":
            raise AssertionError(
                "Vehicle did not enter RETURNING state."
            )

        print()
        print("Return mission started.")
        print(
            f"Vehicle status: {vehicle.status}"
        )

        # =========================================================
        # 7. Calculate route back to original edge
        #
        # EmergencyResponseRouter expects an EmergencyState as
        # destination, so create a return mission object.
        # =========================================================

        return_emergency = EmergencyState(
            emergency_id="E_RETURN_001",
            emergency_type="RETURN",
            location=original_edge,
            severity="LOW",
            creation_time=0.0
        )

        simulation_state.emergencies[
            return_emergency.emergency_id
        ] = return_emergency

        return_route, return_distance = (
            response_router.plan_route(
                vehicle_id=vehicle_id,
                emergency_id=return_emergency.emergency_id
            )
        )

        if not return_route:
            raise AssertionError(
                "Return route is empty."
            )

        print()
        print(
            f"Return route edges: "
            f"{len(return_route)}"
        )
        print(
            f"Return route distance: "
            f"{return_distance:.2f}"
        )

        # =========================================================
        # 8. Apply return route
        # =========================================================

        apply_route(
            vehicle_id,
            return_route
        )

        print()
        print(
            "Return route assigned to SUMO successfully."
        )

        # =========================================================
        # 9. Execute return route
        # =========================================================

        return_reached = False

        print()
        print("Returning to original location:")

        for step in range(150):

            traci.simulationStep()

            manager.synchronize_with_sumo()

            vehicle = simulation_state.emergency_vehicles[
                vehicle_id
            ]

            print(
                f"Return step {step + 1}: "
                f"edge={vehicle.current_edge}, "
                f"speed={vehicle.speed:.2f}, "
                f"position={vehicle.position:.2f}, "
                f"status={vehicle.status}"
            )

            if (
                vehicle.status == "RETURNING"
                and vehicle.current_edge
                == original_edge
            ):

                return_reached = True

                break

        if not return_reached:
            raise AssertionError(
                "Vehicle did not reach its return destination."
            )

        # =========================================================
        # 10. RETURNING -> AVAILABLE
        # =========================================================

        manager.release_vehicle(
            vehicle_id
        )

        vehicle = simulation_state.emergency_vehicles[
            vehicle_id
        ]

        print()
        print("Return destination reached.")
        print(
            f"Final vehicle status: {vehicle.status}"
        )
        print(
            f"Final assignment: "
            f"{vehicle.assigned_emergency}"
        )

        # =========================================================
        # 11. Final lifecycle validation
        # =========================================================

        if vehicle.status != "AVAILABLE":
            raise AssertionError(
                f"Expected AVAILABLE, got {vehicle.status}"
            )

        if vehicle.assigned_emergency is not None:
            raise AssertionError(
                "Emergency assignment was not cleared."
            )

        if vehicle.current_edge != original_edge:
            raise AssertionError(
                "Vehicle is not at its return destination."
            )

        # =========================================================
        # 12. Verify AVAILABLE survives synchronization
        # =========================================================

        print()
        print(
            "Verifying final AVAILABLE state preservation..."
        )

        for step in range(3):

            traci.simulationStep()

            manager.synchronize_with_sumo()

            vehicle = simulation_state.emergency_vehicles[
                vehicle_id
            ]

            print(
                f"Final verification {step + 1}: "
                f"edge={vehicle.current_edge}, "
                f"status={vehicle.status}, "
                f"assignment={vehicle.assigned_emergency}"
            )

            if vehicle.status != "AVAILABLE":
                raise AssertionError(
                    "SUMO synchronization changed "
                    f"AVAILABLE to {vehicle.status}."
                )

            if vehicle.assigned_emergency is not None:
                raise AssertionError(
                    "Released vehicle regained "
                    "an emergency assignment."
                )

        print()
        print(
            "Complete emergency vehicle lifecycle "
            "validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    main()