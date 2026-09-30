import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.core.simulation_synchronization_manager import (
    SimulationSynchronizationManager
)


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def test_simulation_synchronization_manager():

    simulation_state = SimulationState()

    synchronization_manager = (
        SimulationSynchronizationManager(
            simulation_state
        )
    )

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:

        for step in range(10):

            result = synchronization_manager.step(
                max_new_roads=10
            )

            sumo_active_ids = set(
                traci.vehicle.getIDList()
            )

            python_active_ids = {
                vehicle_id
                for vehicle_id, vehicle
                in simulation_state.vehicles.items()
                if vehicle.status == "ACTIVE"
            }

            emergency_ids = set(
                result["emergency_vehicle_ids"]
            )

            assert python_active_ids == sumo_active_ids

            assert emergency_ids.issubset(
                sumo_active_ids
            )

            assert (
                simulation_state.simulation_time
                == traci.simulation.getTime()
            )

            assert len(
                simulation_state.roads
            ) >= 0

            print(
                f"Step {step + 1}: "
                f"time={simulation_state.simulation_time}, "
                f"vehicles={len(python_active_ids)}, "
                f"emergency_vehicles={len(emergency_ids)}, "
                f"roads={len(simulation_state.roads)}"
            )

        print(
            "Unified simulation synchronization "
            "validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    test_simulation_synchronization_manager()