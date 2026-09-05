from Simulation.connection.sumo_connection import SumoConnection
from Simulation.state.simulation_state import SimulationState
from Simulation.traffic.traffic_state_manager import TrafficStateManager

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

        traffic_manager = None
        simulation_state = None

        # --------------------------------------------------
        # Find an Active Road
        # --------------------------------------------------

        traci.simulationStep()

        simulation_state = SimulationState(
            simulation_time=traci.simulation.getTime()
        )

        traffic_manager = TrafficStateManager(
            simulation_state
        )

        active_roads = (
            traffic_manager.discover_active_roads(
                max_roads=1
            )
        )

        print(
            f"\nInitial active roads: {active_roads}"
        )

        if not active_roads:

            print(
                "No active road found for this test."
            )
            return

        road_id = active_roads[0]

        # --------------------------------------------------
        # Initialize the Road
        # --------------------------------------------------

        traffic_manager.initialize_roads(
            [road_id]
        )

        road_state = simulation_state.roads[road_id]

        print("\nInitial Road State:")
        print(road_state)

        # --------------------------------------------------
        # Dynamic Refresh Test
        # --------------------------------------------------

        road_became_inactive = False

        for step in range(10):

            traci.simulationStep()

            simulation_state.simulation_time = (
                traci.simulation.getTime()
            )

            # Update the already stored road
            traffic_manager.update_roads()

            current_vehicle_count = (
                traci.edge.getLastStepVehicleNumber(
                    road_id
                )
            )

            print(
                f"\nStep {step + 1}: "
                f"time={simulation_state.simulation_time}, "
                f"SUMO vehicles={current_vehicle_count}, "
                f"State vehicles={road_state.vehicle_count}"
            )

            # --------------------------------------------------
            # Detect when road becomes inactive
            # --------------------------------------------------

            if current_vehicle_count == 0:

                road_became_inactive = True

                print(
                    f"Road {road_id} is now inactive."
                )

                # Validate state was refreshed
                assert road_state.vehicle_count == 0

                # Validate against SUMO
                assert (
                    road_state.current_speed
                    == traci.edge.getLastStepMeanSpeed(
                        road_id
                    )
                )

                assert (
                    road_state.travel_time
                    == traci.edge.getTraveltime(
                        road_id
                    )
                )

                print(
                    "Inactive-road state refresh validated!"
                )

                break

        # --------------------------------------------------
        # Final Validation
        # --------------------------------------------------

        print("\nInactive Road Refresh Validation:")

        assert road_id in simulation_state.roads

        if road_became_inactive:

            assert road_state.vehicle_count == 0

            print(
                "Inactive-road refresh validation successful!"
            )

        else:

            print(
                "Road remained active during all test steps."
            )

            print(
                "Inactive-road transition was not observed, "
                "so this specific transition was not validated."
            )

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()