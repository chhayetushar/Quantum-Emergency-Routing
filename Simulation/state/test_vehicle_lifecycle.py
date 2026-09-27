import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.vehicle_state_manager import VehicleStateManager


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def test_vehicle_lifecycle():

    simulation_state = SimulationState()
    manager = VehicleStateManager(simulation_state)

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:
        found_inactive_vehicle = False

        for step in range(300):

            traci.simulationStep()

            active_vehicle_ids = set(
                manager.synchronize_with_sumo()
            )

            arrived_vehicle_ids = set(
                traci.simulation.getArrivedIDList()
            )

            if arrived_vehicle_ids:
                print(
                    f"Step {step + 1}: "
                    f"Vehicles arrived = "
                    f"{arrived_vehicle_ids}"
                )

            for vehicle_id in arrived_vehicle_ids:

                assert vehicle_id in (
                    simulation_state.vehicles
                )

                vehicle = simulation_state.vehicles[
                    vehicle_id
                ]

                assert vehicle.status == "INACTIVE"

                found_inactive_vehicle = True

                print(
                    f"{vehicle_id} → "
                    f"status={vehicle.status}"
                )

                break

            if found_inactive_vehicle:
                break

        assert found_inactive_vehicle, (
            "No vehicle completed its trip within "
            "300 simulation steps."
        )

        print(
            "Vehicle lifecycle synchronization "
            "validation successful!"
        )

    finally:
        traci.close()


if __name__ == "__main__":
    test_vehicle_lifecycle()