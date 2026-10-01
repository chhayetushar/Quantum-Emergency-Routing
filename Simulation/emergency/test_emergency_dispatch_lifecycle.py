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
    Wait until SUMO contains an emergency vehicle and synchronize it.
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
        # 2. Wait for emergency vehicle
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
        # 3. Validate initial state
        # ---------------------------------------------------------

        if vehicle.status != "AVAILABLE":
            raise AssertionError(
                f"Expected AVAILABLE, got {vehicle.status}"
            )

        if vehicle.assigned_emergency is not None:
            raise AssertionError(
                "Vehicle unexpectedly has an assigned emergency."
            )

        # ---------------------------------------------------------
        # 4. Create emergency
        # ---------------------------------------------------------

        emergency_edge = None

        for edge_id in graph.edges:
            if edge_id != vehicle.current_edge:
                emergency_edge = edge_id
                break

        if emergency_edge is None:
            raise RuntimeError(
                "Could not find a destination emergency edge."
            )

        emergency = EmergencyState(
            emergency_id="E_DISPATCH_001",
            emergency_type="TRAFFIC_ACCIDENT",
            location=emergency_edge,
            severity="HIGH",
            creation_time=0.0
        )

        simulation_state.emergencies[
            emergency.emergency_id
        ] = emergency

        print(
            f"Emergency edge: {emergency.location}"
        )

        # ---------------------------------------------------------
        # 5. Assign emergency
        # ---------------------------------------------------------

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
                f"Expected ASSIGNED, got {vehicle.status}"
            )

        if vehicle.assigned_emergency != emergency.emergency_id:
            raise AssertionError(
                "Emergency assignment was not recorded correctly."
            )

        print()
        print("Emergency assigned successfully.")
        print(f"Vehicle status: {vehicle.status}")
        print(
            f"Assigned emergency: "
            f"{vehicle.assigned_emergency}"
        )

        # ---------------------------------------------------------
        # 6. Calculate emergency response route
        # ---------------------------------------------------------

        response_router = EmergencyResponseRouter(
            simulation_state=simulation_state,
            graph=graph
        )

        route, total_distance = response_router.plan_route(
            vehicle_id=vehicle_id,
            emergency_id=emergency.emergency_id
        )

        if not route:
            raise AssertionError(
                "Emergency response route is empty."
            )

        print()
        print(
            f"Emergency route edges: {len(route)}"
        )
        print(
            f"Emergency route distance: "
            f"{total_distance:.2f}"
        )

        print()
        print("Emergency route:")

        for edge in route:
            print(edge.edge_id)

        # ---------------------------------------------------------
        # 7. Convert route to SUMO edge IDs
        # ---------------------------------------------------------

        sumo_route = RouteConverter.to_sumo_edge_ids(
            route
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
        # 8. Apply route to SUMO
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
                "SUMO did not accept the expected emergency route."
            )

        print()
        print(
            "Emergency route assigned to SUMO vehicle successfully."
        )

        # ---------------------------------------------------------
        # 9. Transition ASSIGNED -> EN_ROUTE
        # ---------------------------------------------------------

        manager.update_status(
            vehicle_id=vehicle_id,
            new_status="EN_ROUTE"
        )

        vehicle = simulation_state.emergency_vehicles[
            vehicle_id
        ]

        if vehicle.status != "EN_ROUTE":
            raise AssertionError(
                f"Expected EN_ROUTE, got {vehicle.status}"
            )

        print(
            f"Vehicle status after route assignment: "
            f"{vehicle.status}"
        )

        # ---------------------------------------------------------
        # 10. Execute route in SUMO
        # ---------------------------------------------------------

        print()
        print("Emergency route execution:")

        initial_edge = vehicle.current_edge

        movement_detected = False

        for step in range(10):

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

            if (
                vehicle.current_edge != initial_edge
                or vehicle.position > 0
                or vehicle.speed > 0
            ):
                movement_detected = True

            # Mission state must remain EN_ROUTE.
            if vehicle.status != "EN_ROUTE":
                raise AssertionError(
                    "SUMO synchronization changed the "
                    f"mission status unexpectedly: "
                    f"{vehicle.status}"
                )

            # Assignment must also survive synchronization.
            if (
                vehicle.assigned_emergency
                != emergency.emergency_id
            ):
                raise AssertionError(
                    "SUMO synchronization lost the "
                    "emergency assignment."
                )

        # ---------------------------------------------------------
        # 11. Final validation
        # ---------------------------------------------------------

        if not movement_detected:
            raise AssertionError(
                "Emergency vehicle did not show movement "
                "after route assignment."
            )

        print()
        print(
            "Emergency dispatch lifecycle validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    main()