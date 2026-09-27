import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def test_sumo_emergency_vehicle_sync():

    simulation_state = SimulationState()
    manager = EmergencyVehicleManager(simulation_state)

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    found_vehicle = None

    try:
        for _ in range(300):

            traci.simulationStep()

            emergency_vehicle_ids = (
                manager.synchronize_with_sumo()
            )

            if emergency_vehicle_ids:
                found_vehicle = emergency_vehicle_ids[0]

                vehicle = (
                    simulation_state.emergency_vehicles[
                        found_vehicle
                    ]
                )

                sumo_edge = traci.vehicle.getRoadID(
                    found_vehicle
                )

                sumo_speed = traci.vehicle.getSpeed(
                    found_vehicle
                )

                sumo_position = traci.vehicle.getLanePosition(
                    found_vehicle
                )

                assert vehicle.current_edge == sumo_edge
                assert vehicle.speed == sumo_speed
                assert vehicle.position == sumo_position

                print("\nEmergency vehicle synchronized!")
                print("--------------------------------")
                print(f"Vehicle ID : {vehicle.vehicle_id}")
                print(f"Type       : {vehicle.vehicle_type}")
                print(f"Edge       : {vehicle.current_edge}")
                print(f"Speed      : {vehicle.speed}")
                print(f"Position   : {vehicle.position}")
                print(f"Status     : {vehicle.status}")

                break

        assert found_vehicle is not None, (
            "No emergency vehicle was synchronized "
            "within 300 simulation steps."
        )

        print(
            "\nSUMO emergency vehicle synchronization "
            "validation successful!"
        )

    finally:
        traci.close()


if __name__ == "__main__":
    test_sumo_emergency_vehicle_sync()