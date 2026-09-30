import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.emergency_state import EmergencyState
from Simulation.state.vehicle_state_manager import VehicleStateManager
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def test_emergency_state_preservation():

    simulation_state = SimulationState()

    vehicle_manager = VehicleStateManager(
        simulation_state
    )

    emergency_manager = EmergencyVehicleManager(
        simulation_state
    )

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:

        found_emergency_vehicle = False

        for _ in range(300):

            traci.simulationStep()

            # Synchronize all vehicles first
            vehicle_manager.synchronize_with_sumo()

            # Synchronize emergency vehicles
            emergency_vehicle_ids = (
                emergency_manager.synchronize_with_sumo()
            )

            if not emergency_vehicle_ids:
                continue

            vehicle_id = emergency_vehicle_ids[0]

            vehicle = (
                simulation_state.emergency_vehicles[
                    vehicle_id
                ]
            )

            # Create a dummy emergency relationship
            simulation_state.emergencies["E001"] = EmergencyState(
                emergency_id="E001",
                emergency_type="ACCIDENT",
                location=vehicle.current_edge,
                severity="HIGH",
                creation_time=(
                    simulation_state.simulation_time
                    if hasattr(
                        simulation_state,
                        "simulation_time"
                    )
                    else 0.0
                )
            )

            # Simulate an assigned emergency vehicle
            vehicle.assigned_emergency = "E001"
            vehicle.status = "EN_ROUTE"

            old_assignment = vehicle.assigned_emergency
            old_status = vehicle.status

            # Synchronize again
            emergency_manager.synchronize_with_sumo()

            updated_vehicle = (
                simulation_state.emergency_vehicles[
                    vehicle_id
                ]
            )

            # Mission state must remain unchanged
            assert (
                updated_vehicle.assigned_emergency
                == old_assignment
            )

            assert (
                updated_vehicle.status
                == old_status
            )

            # Movement state must still be synchronized
            assert (
                updated_vehicle.current_edge
                == traci.vehicle.getRoadID(vehicle_id)
            )

            assert (
                updated_vehicle.speed
                == traci.vehicle.getSpeed(vehicle_id)
            )

            assert (
                updated_vehicle.position
                == traci.vehicle.getLanePosition(vehicle_id)
            )

            print("\nEmergency state preservation verified!")
            print("--------------------------------")
            print(f"Vehicle ID         : {vehicle_id}")
            print(f"Status              : {updated_vehicle.status}")
            print(
                f"Assigned emergency : "
                f"{updated_vehicle.assigned_emergency}"
            )
            print(
                f"Current edge       : "
                f"{updated_vehicle.current_edge}"
            )
            print(
                f"Speed              : "
                f"{updated_vehicle.speed}"
            )
            print(
                f"Position           : "
                f"{updated_vehicle.position}"
            )

            found_emergency_vehicle = True
            break

        assert found_emergency_vehicle, (
            "No emergency vehicle appeared within "
            "300 simulation steps."
        )

        print(
            "\nEmergency state preservation "
            "validation successful!"
        )

    finally:
        traci.close()


if __name__ == "__main__":
    test_emergency_state_preservation()