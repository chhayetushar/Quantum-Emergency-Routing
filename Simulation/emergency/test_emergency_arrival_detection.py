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
    Run SUMO until an emergency vehicle appears and synchronize it.
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

        # ---------------------------------------------------------
        # 1. Build road graph
        # ---------------------------------------------------------

        graph.build_from_sumo()

        print(f"Graph nodes: {graph.node_count()}")
        print(f"Graph edges: {graph.edge_count()}")

        # ---------------------------------------------------------
        # 2. Find emergency vehicle
        # ---------------------------------------------------------

        vehicle_id = find_emergency_vehicle(
            manager,
            simulation_state
        )

        vehicle = simulation_state.emergency_vehicles[
            vehicle_id
        ]

        print()
        print(f"Emergency vehicle: {vehicle_id}")
        print(f"Vehicle type: {vehicle.vehicle_type}")
        print(f"Current edge: {vehicle.current_edge}")
        print(f"Initial status: {vehicle.status}")

        # ---------------------------------------------------------
        # 3. Select an emergency destination
        #
        # Use a reachable destination so the vehicle can actually
        # arrive there during the integration test.
        # ---------------------------------------------------------

        response_router = EmergencyResponseRouter(
            simulation_state=simulation_state,
            graph=graph
        )

        destination_edge = None
        destination_route = None
        destination_distance = None

        # Try graph edges until we find a reasonably short,
        # reachable destination.
        candidate_edges = list(graph.edges.keys())

        for candidate_edge in candidate_edges:

            if candidate_edge == vehicle.current_edge:
                continue

            emergency = EmergencyState(
                emergency_id="E_ARRIVAL_TEST",
                emergency_type="TRAFFIC_ACCIDENT",
                location=candidate_edge,
                severity="HIGH",
                creation_time=0.0
            )

            simulation_state.emergencies[
                emergency.emergency_id
            ] = emergency

            # The vehicle must be assigned before the response
            # router can plan its mission.
            manager.assign_emergency(
                vehicle_id=vehicle_id,
                emergency_id=emergency.emergency_id
            )

            manager.update_status(
                vehicle_id=vehicle_id,
                new_status="ASSIGNED"
            )

            try:

                route, distance = response_router.plan_route(
                    vehicle_id=vehicle_id,
                    emergency_id=emergency.emergency_id
                )

                if route and len(route) <= 20:
                    destination_edge = candidate_edge
                    destination_route = route
                    destination_distance = distance
                    break

            except Exception:
                pass

            # Reset failed candidate.
            vehicle.status = "AVAILABLE"
            vehicle.assigned_emergency = None

            simulation_state.emergencies.pop(
                emergency.emergency_id,
                None
            )

        if destination_edge is None:
            raise RuntimeError(
                "Could not find a suitable reachable "
                "emergency destination."
            )

        emergency = simulation_state.emergencies[
            "E_ARRIVAL_TEST"
        ]

        print()
        print(
            f"Emergency edge: {emergency.location}"
        )

        print(
            f"Emergency route edges: "
            f"{len(destination_route)}"
        )

        print(
            f"Emergency route distance: "
            f"{destination_distance:.2f}"
        )

        # ---------------------------------------------------------
        # 4. Convert route to SUMO route
        # ---------------------------------------------------------

        sumo_route = RouteConverter.to_sumo_edge_ids(
            destination_route
        )

        if not sumo_route:
            raise AssertionError(
                "Converted SUMO route is empty."
            )

        print()
        print("SUMO route:")

        for edge_id in sumo_route:
            print(edge_id)

        # ---------------------------------------------------------
        # 5. Apply route
        # ---------------------------------------------------------

        traci.vehicle.setRoute(
            vehicle_id,
            sumo_route
        )

        applied_route = list(
            traci.vehicle.getRoute(vehicle_id)
        )

        if applied_route != sumo_route:
            raise AssertionError(
                "SUMO route does not match expected route."
            )

        # ---------------------------------------------------------
        # 6. ASSIGNED -> EN_ROUTE
        # ---------------------------------------------------------

        manager.update_status(
            vehicle_id=vehicle_id,
            new_status="EN_ROUTE"
        )

        vehicle = simulation_state.emergency_vehicles[
            vehicle_id
        ]

        print()
        print(
            f"Vehicle status after dispatch: "
            f"{vehicle.status}"
        )

        if vehicle.status != "EN_ROUTE":
            raise AssertionError(
                "Vehicle did not enter EN_ROUTE state."
            )

        # ---------------------------------------------------------
        # 7. Execute until destination edge is reached
        # ---------------------------------------------------------

        arrival_detected = False

        print()
        print("Emergency response execution:")

        for step in range(100):

            traci.simulationStep()

            manager.synchronize_with_sumo()

            vehicle = simulation_state.emergency_vehicles[
                vehicle_id
            ]

            print(
                f"Step {step + 1}: "
                f"edge={vehicle.current_edge}, "
                f"speed={vehicle.speed:.2f}, "
                f"position={vehicle.position:.2f}, "
                f"status={vehicle.status}"
            )

            # -----------------------------------------------------
            # Arrival condition:
            # vehicle has reached the emergency destination edge.
            # -----------------------------------------------------

            if (
                vehicle.status == "EN_ROUTE"
                and vehicle.current_edge
                == emergency.location
            ):

                manager.update_status(
                    vehicle_id=vehicle_id,
                    new_status="AT_SCENE"
                )

                arrival_detected = True

                print()
                print(
                    "Emergency vehicle reached "
                    "the emergency location."
                )

                print(
                    f"Vehicle status: {vehicle.status}"
                )

                break

        # ---------------------------------------------------------
        # 8. Validate arrival transition
        # ---------------------------------------------------------

        if not arrival_detected:
            raise AssertionError(
                "Emergency vehicle did not reach "
                "the emergency destination edge."
            )

        vehicle = simulation_state.emergency_vehicles[
            vehicle_id
        ]

        if vehicle.status != "AT_SCENE":
            raise AssertionError(
                f"Expected AT_SCENE, got {vehicle.status}"
            )

        if vehicle.assigned_emergency != emergency.emergency_id:
            raise AssertionError(
                "Emergency assignment was lost after arrival."
            )

        if vehicle.current_edge != emergency.location:
            raise AssertionError(
                "Vehicle is not on the emergency destination edge."
            )

        # ---------------------------------------------------------
        # 9. Verify synchronization preserves AT_SCENE
        # ---------------------------------------------------------

        print()
        print(
            "Verifying AT_SCENE state preservation..."
        )

        for step in range(3):

            traci.simulationStep()

            manager.synchronize_with_sumo()

            vehicle = simulation_state.emergency_vehicles[
                vehicle_id
            ]

            print(
                f"Post-arrival step {step + 1}: "
                f"edge={vehicle.current_edge}, "
                f"status={vehicle.status}, "
                f"assignment={vehicle.assigned_emergency}"
            )

            if vehicle.status != "AT_SCENE":
                raise AssertionError(
                    "SUMO synchronization changed "
                    f"AT_SCENE to {vehicle.status}."
                )

            if (
                vehicle.assigned_emergency
                != emergency.emergency_id
            ):
                raise AssertionError(
                    "SUMO synchronization lost "
                    "the emergency assignment."
                )

        print()
        print(
            "Emergency arrival detection validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    main()