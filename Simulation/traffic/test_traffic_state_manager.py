from Simulation.connection.sumo_connection import SumoConnection
from Simulation.state.simulation_state import SimulationState
from Simulation.traffic.traffic_state_manager import (
    TrafficStateManager
)

import traci


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
SUMO_CONFIG = r"D:\Mini_Project\Quantum-Emergency-Routing\sumo\emergency_simulation.sumocfg"

SAMPLE_ROAD_COUNT = 10


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
        # Advance Simulation
        # --------------------------------------------------

        traci.simulationStep()

        simulation_state = SimulationState(
            simulation_time=traci.simulation.getTime()
        )

        print("\nSimulation time:")
        print(simulation_state.simulation_time)

        # --------------------------------------------------
        # Create Traffic State Manager
        # --------------------------------------------------

        traffic_manager = TrafficStateManager(
            simulation_state
        )

        # --------------------------------------------------
        # Discover Active Roads
        # --------------------------------------------------

        active_road_ids = (
            traffic_manager.discover_active_roads(
                max_roads=SAMPLE_ROAD_COUNT
            )
        )

        print(
            f"\nActive roads discovered: "
            f"{len(active_road_ids)}"
        )

        print("Active road IDs:")
        print(active_road_ids)

        if not active_road_ids:

            print(
                "No active roads found at this "
                "simulation step."
            )

            return

        # --------------------------------------------------
        # Initialize Active Roads
        # --------------------------------------------------

        traffic_manager.initialize_roads(
            active_road_ids
        )

        print(
            f"\nRoads initialized in "
            f"SimulationState: "
            f"{len(simulation_state.roads)}"
        )

        # --------------------------------------------------
        # Display Roads
        # --------------------------------------------------

        print("\nActive Road States:")

        for road_id, road in simulation_state.roads.items():

            print(
                f"{road_id} -> "
                f"vehicles={road.vehicle_count}, "
                f"speed={road.current_speed}, "
                f"speed_limit={road.speed_limit}, "
                f"congestion={road.congestion_level}"
            )

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        print("\nActive Road Discovery Validation:")

        assert (
            len(active_road_ids)
            == len(simulation_state.roads)
        )

        for road_id in active_road_ids:

            assert road_id in simulation_state.roads

            vehicle_count = (
                traci.edge.getLastStepVehicleNumber(
                    road_id
                )
            )

            assert vehicle_count > 0

        print(
            "Active road discovery validation successful!"
        )

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()