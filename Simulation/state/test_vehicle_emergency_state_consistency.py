import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.vehicle_state_manager import VehicleStateManager
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def test_vehicle_emergency_state_consistency():

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

            # Track every active SUMO vehicle
            vehicle_manager.synchronize_with_sumo()

            # Track emergency vehicles specifically
            emergency_vehicle_ids = (
                emergency_manager.synchronize_with_sumo()
            )

            for vehicle_id in emergency_vehicle_ids:

                found_emergency_vehicle = True

                general_vehicle = (
                    simulation_state.vehicles[
                        vehicle_id
                    ]
                )

                emergency_vehicle = (
                    simulation_state.emergency_vehicles[
                        vehicle_id
                    ]
                )

                assert (
                    general_vehicle.vehicle_id
                    == emergency_vehicle.vehicle_id
                )

                assert (
                    general_vehicle.vehicle_type.lower()
                    == emergency_vehicle.vehicle_type.lower()
                )

                assert (
                    general_vehicle.current_edge
                    == emergency_vehicle.current_edge
                )

                assert (
                    general_vehicle.speed
                    == emergency_vehicle.speed
                )

                assert (
                    general_vehicle.position
                    == emergency_vehicle.position
                )

                print(
                    "\nVehicle state consistency verified"
                )
                print("--------------------------------")
                print(
                    f"Vehicle ID : "
                    f"{vehicle_id}"
                )
                print(
                    f"General type : "
                    f"{general_vehicle.vehicle_type}"
                )
                print(
                    f"Emergency type : "
                    f"{emergency_vehicle.vehicle_type}"
                )
                print(
                    f"Edge : "
                    f"{general_vehicle.current_edge}"
                )
                print(
                    f"Speed : "
                    f"{general_vehicle.speed}"
                )
                print(
                    f"Position : "
                    f"{general_vehicle.position}"
                )

                break

            if found_emergency_vehicle:
                break

        assert found_emergency_vehicle, (
            "No emergency vehicle appeared during "
            "the synchronization test."
        )

        print(
            "\nVehicle and emergency vehicle "
            "state consistency validation successful!"
        )

    finally:
        traci.close()


if __name__ == "__main__":
    test_vehicle_emergency_state_consistency()