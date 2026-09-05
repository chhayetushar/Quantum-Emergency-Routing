from Simulation.connection.sumo_connection import SumoConnection
from Simulation.traffic.road_state_updater import create_road_state
from Simulation.traffic.road_state_updater import update_road_state

import traci


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
SUMO_CONFIG = r"D:\Mini_Project\Quantum-Emergency-Routing\sumo\emergency_simulation.sumocfg"


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

        # Initial simulation step
        traci.simulationStep()

        # Find an active road
        edge_ids = traci.edge.getIDList()

        active_road_ids = []

        for edge_id in edge_ids:

            vehicle_count = traci.edge.getLastStepVehicleNumber(
                edge_id
            )

            if vehicle_count > 0:
                active_road_ids.append(edge_id)

        if not active_road_ids:

            print("No active roads found.")
            return

        edge_id = active_road_ids[0]

        print(f"\nSelected road: {edge_id}")

        # Create RoadState
        road_state = create_road_state(edge_id)

        print("\nInitial RoadState:")
        print(road_state)

        # --------------------------------------------------
        # Update RoadState
        # --------------------------------------------------

        for step in range(5):

            traci.simulationStep()

            update_road_state(road_state)

            print(
                f"\nStep {step + 1}:"
            )

            print(
                f"Vehicle count: {road_state.vehicle_count}"
            )

            print(
                f"Current speed: {road_state.current_speed}"
            )

            print(
                f"Travel time: {road_state.travel_time}"
            )

            print(
                f"Congestion: {road_state.congestion_level}"
            )

        print(
            "\nReusable road-state updater validation successful!"
        )

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()