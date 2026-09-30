import traci

from Simulation.state.simulation_state import SimulationState
from Simulation.state.vehicle_synchronization_manager import (
    VehicleSynchronizationManager
)


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def test_vehicle_synchronization_manager():

    simulation_state = SimulationState()

    synchronization_manager = VehicleSynchronizationManager(
        simulation_state
    )

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:

        for step in range(10):

            traci.simulationStep()

            (
                all_vehicle_ids,
                emergency_vehicle_ids
            ) = synchronization_manager.synchronize()

            sumo_vehicle_ids = set(
                traci.vehicle.getIDList()
            )

            python_vehicle_ids = set(
                simulation_state.vehicles.keys()
            )

            # --------------------------------------------------
            # Validate ALL vehicle tracking
            # --------------------------------------------------

            assert set(all_vehicle_ids) == sumo_vehicle_ids

            # Every currently active SUMO vehicle must be
            # represented in the Python state.
            for vehicle_id in sumo_vehicle_ids:

                assert vehicle_id in simulation_state.vehicles

                vehicle = simulation_state.vehicles[
                    vehicle_id
                ]

                assert vehicle.status == "ACTIVE"

            # --------------------------------------------------
            # Validate emergency vehicle relationship
            # --------------------------------------------------

            for vehicle_id in emergency_vehicle_ids:

                assert vehicle_id in simulation_state.vehicles

                assert (
                    vehicle_id
                    in simulation_state.emergency_vehicles
                )

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
                f"Step {step + 1}: "
                f"all vehicles={len(all_vehicle_ids)}, "
                f"emergency vehicles="
                f"{len(emergency_vehicle_ids)}"
            )

        print(
            "Unified vehicle synchronization "
            "validation successful!"
        )

    finally:

        traci.close()


if __name__ == "__main__":
    test_vehicle_synchronization_manager()