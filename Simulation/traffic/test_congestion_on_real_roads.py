from Simulation.connection.sumo_connection import SumoConnection
from Simulation.state.simulation_state import SimulationState
from Simulation.traffic.road_state_updater import create_road_state
from Simulation.traffic.congestion import calculate_congestion_level

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
        # Find Roads With Active Traffic
        # --------------------------------------------------

        edge_ids = traci.edge.getIDList()

        active_road_ids = []

        for edge_id in edge_ids:

            vehicle_count = traci.edge.getLastStepVehicleNumber(
                edge_id
            )

            if vehicle_count > 0:
                active_road_ids.append(edge_id)

        print(
            f"\nActive roads found: {len(active_road_ids)}"
        )

        # --------------------------------------------------
        # Select Sample Roads
        # --------------------------------------------------

        selected_road_ids = active_road_ids[:SAMPLE_ROAD_COUNT]

        if not selected_road_ids:

            print(
                "No roads with active traffic were found."
            )
            return

        print(
            f"Testing {len(selected_road_ids)} "
            "active roads..."
        )

        # --------------------------------------------------
        # Create Road States
        # --------------------------------------------------

        for edge_id in selected_road_ids:

            road_state = create_road_state(edge_id)

            simulation_state.roads[edge_id] = road_state

        # --------------------------------------------------
        # Display Congestion Information
        # --------------------------------------------------

        print("\nRoad Congestion Information:")

        for road_id, road in simulation_state.roads.items():

            if road.speed_limit > 0:

                speed_ratio = (
                    road.current_speed
                    / road.speed_limit
                )

            else:

                speed_ratio = 0.0

            print(
                f"{road_id} -> "
                f"vehicles={road.vehicle_count}, "
                f"speed={road.current_speed}, "
                f"speed_limit={road.speed_limit}, "
                f"ratio={speed_ratio:.3f}, "
                f"congestion={road.congestion_level}"
            )

        # --------------------------------------------------
        # Congestion Classification Validation
        # --------------------------------------------------

        print(
            "\nReal-Road Congestion Validation:"
        )

        for road_id, road in simulation_state.roads.items():

            expected_level = calculate_congestion_level(
                current_speed=road.current_speed,
                speed_limit=road.speed_limit
            )

            assert road.congestion_level == expected_level

        print(
            "Real-road congestion classification "
            "validation successful!"
        )

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()