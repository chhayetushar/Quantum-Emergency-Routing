from Simulation.connection.sumo_connection import SumoConnection
from Simulation.state.simulation_state import SimulationState
from Simulation.traffic.traffic_state_manager import (
    TrafficStateManager
)

import traci


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
SUMO_CONFIG = r"D:\Mini_Project\Quantum-Emergency-Routing\sumo\emergency_simulation.sumocfg"

MAX_ACTIVE_ROADS = 10


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
        # Initial Simulation Step
        # --------------------------------------------------

        traci.simulationStep()

        simulation_state = SimulationState(
            simulation_time=traci.simulation.getTime()
        )

        traffic_manager = TrafficStateManager(
            simulation_state
        )

        # --------------------------------------------------
        # Initial Active-Road Discovery
        # --------------------------------------------------

        new_roads = (
            traffic_manager
            .discover_and_initialize_active_roads(
                max_roads=MAX_ACTIVE_ROADS
            )
        )

        print(
            f"\nTime {simulation_state.simulation_time}:"
        )

        print(
            f"New active roads initialized: "
            f"{len(new_roads)}"
        )

        print(
            f"Total stored roads: "
            f"{len(simulation_state.roads)}"
        )

        # --------------------------------------------------
        # Dynamic Discovery
        # --------------------------------------------------

        for step in range(5):

            traci.simulationStep()

            simulation_state.simulation_time = (
                traci.simulation.getTime()
            )

            new_roads = (
                traffic_manager
                .discover_and_initialize_active_roads(
                    max_roads=MAX_ACTIVE_ROADS
                )
            )

            traffic_manager.update_roads()

            print(
                f"\nTime {simulation_state.simulation_time}:"
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
        # Validation
        # --------------------------------------------------

        print("\nDynamic Road Discovery Validation:")

        active_road_ids = set(
            traffic_manager.discover_active_roads()
        )

        stored_road_ids = set(
            simulation_state.roads.keys()
        )

        # Every stored road must have a valid ID
        for road_id in stored_road_ids:

            assert road_id != ""

            assert (
                simulation_state.roads[road_id].road_id
                == road_id
            )

        # No duplicate road IDs can exist in the dictionary
        assert len(stored_road_ids) == len(
            simulation_state.roads
        )

        print(
            f"Currently active roads in SUMO: "
            f"{len(active_road_ids)}"
        )

        print(
            f"Roads stored in SimulationState: "
            f"{len(stored_road_ids)}"
        )

        print(
            "Dynamic road discovery validation successful!"
        )

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()