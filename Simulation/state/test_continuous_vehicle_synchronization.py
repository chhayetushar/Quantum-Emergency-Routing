import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.vehicle_state_manager import VehicleStateManager


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def test_continuous_vehicle_synchronization():

    simulation_state = SimulationState()
    manager = VehicleStateManager(simulation_state)

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:
        for step in range(100):

            traci.simulationStep()

            sumo_active_ids = set(
                traci.vehicle.getIDList()
            )

            manager.synchronize_with_sumo()

            python_active_ids = {
                vehicle_id
                for vehicle_id, vehicle
                in simulation_state.vehicles.items()
                if vehicle.status == "ACTIVE"
            }

            assert python_active_ids == sumo_active_ids

            for vehicle_id, vehicle in (
                simulation_state.vehicles.items()
            ):

                if vehicle_id in sumo_active_ids:
                    assert vehicle.status == "ACTIVE"
                else:
                    assert vehicle.status == "INACTIVE"

            if (step + 1) % 20 == 0:
                print(
                    f"Step {step + 1}: "
                    f"SUMO active={len(sumo_active_ids)}, "
                    f"Python active={len(python_active_ids)}, "
                    f"Python total={len(simulation_state.vehicles)}"
                )

        print(
            "Continuous full vehicle synchronization "
            "validation successful!"
        )

    finally:
        traci.close()


if __name__ == "__main__":
    test_continuous_vehicle_synchronization()