import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.vehicle_state_manager import VehicleStateManager


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def test_all_vehicle_tracking():

    simulation_state = SimulationState()
    manager = VehicleStateManager(simulation_state)

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:
        for step in range(5):

            traci.simulationStep()

            sumo_vehicle_ids = set(
                traci.vehicle.getIDList()
            )

            tracked_vehicle_ids = set(
                manager.synchronize_with_sumo()
            )

            assert tracked_vehicle_ids == sumo_vehicle_ids

            for vehicle_id in sumo_vehicle_ids:

                vehicle = simulation_state.vehicles[
                    vehicle_id
                ]

                assert vehicle.vehicle_type == (
                    traci.vehicle.getTypeID(vehicle_id)
                )

                assert vehicle.current_edge == (
                    traci.vehicle.getRoadID(vehicle_id)
                )

                assert vehicle.speed == (
                    traci.vehicle.getSpeed(vehicle_id)
                )

                assert vehicle.position == (
                    traci.vehicle.getLanePosition(vehicle_id)
                )

                assert vehicle.status == "ACTIVE"

            print(
                f"Step {step + 1}: "
                f"{len(sumo_vehicle_ids)} vehicles tracked"
            )

        print(
            "All SUMO vehicle tracking validation successful!"
        )

    finally:
        traci.close()


if __name__ == "__main__":
    test_all_vehicle_tracking()