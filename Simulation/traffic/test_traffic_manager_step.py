from Simulation.connection.sumo_connection import SumoConnection
from Simulation.state.simulation_state import SimulationState
from Simulation.traffic.traffic_state_manager import (
    TrafficStateManager
)

import traci


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
SUMO_CONFIG = r"D:\Mini_Project\Quantum-Emergency-Routing\sumo\emergency_simulation.sumocfg"

MAX_NEW_ROADS_PER_STEP = 10


def main():

    connection = SumoConnection(
        sumo_binary=SUMO_BINARY,
        config_file=SUMO_CONFIG
    )

    try:

        print("Starting SUMO...")

        connection.start()

        print("SUMO started successfully!")
        print("TraCI connection established.")

        # --------------------------------------------------
        # Create Simulation State
        # --------------------------------------------------

        simulation_state = SimulationState()

        traffic_manager = TrafficStateManager(
            simulation_state
        )

        # --------------------------------------------------
        # Advance and Synchronize
        # --------------------------------------------------

        for step_number in range(6):

            new_roads = traffic_manager.step(
                max_new_roads=MAX_NEW_ROADS_PER_STEP
            )

            print(
                f"\nSimulation Step: {step_number + 1}"
            )

            print(
                f"Simulation time: "
                f"{simulation_state.simulation_time}"
            )

            print(
                f"New roads discovered: "
                f"{len(new_roads)}"
            )

            print(
                f"Total stored roads: "
                f"{len(simulation_state.roads)}"
            )

            if new_roads:
                print(
                    f"New road IDs: {new_roads}"
                )

        # --------------------------------------------------
        # Final Validation
        # --------------------------------------------------

        print(
            "\nUnified Traffic-Step Validation:"
        )

        assert simulation_state.simulation_time > 0
        assert len(simulation_state.roads) > 0

        for road_id, road in simulation_state.roads.items():

            assert road_id == road.road_id
            assert road.from_node is not None
            assert road.to_node is not None
            assert road.distance >= 0
            assert road.speed_limit >= 0
            assert road.current_speed >= 0
            assert road.vehicle_count >= 0
            assert road.travel_time >= 0
            assert road.congestion_level != ""

        # Confirm state time matches SUMO time
        assert (
            simulation_state.simulation_time
            == traci.simulation.getTime()
        )

        print(
            "Unified traffic-step validation successful!"
        )

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()