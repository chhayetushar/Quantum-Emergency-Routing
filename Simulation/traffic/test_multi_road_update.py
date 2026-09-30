from Simulation.connection.sumo_connection import SumoConnection
from Simulation.state.simulation_state import SimulationState
from Simulation.traffic.road_state_updater import create_road_state
from Simulation.traffic.road_state_updater import update_road_states

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
        # Initial Simulation Step
        # --------------------------------------------------

        traci.simulationStep()

        simulation_state = SimulationState(
            simulation_time=traci.simulation.getTime()
        )

        print("\nSimulation time:")
        print(simulation_state.simulation_time)

        # --------------------------------------------------
        # Find Active Roads
        # --------------------------------------------------

        edge_ids = traci.edge.getIDList()

        active_road_ids = []

        for edge_id in edge_ids:

            vehicle_count = (
                traci.edge.getLastStepVehicleNumber(edge_id)
            )

            if vehicle_count > 0:
                active_road_ids.append(edge_id)

        print(
            f"\nFound {len(active_road_ids)} "
            "roads with active traffic."
        )

        # --------------------------------------------------
        # Select Roads
        # --------------------------------------------------

        if active_road_ids:

            selected_road_ids = active_road_ids[
                :SAMPLE_ROAD_COUNT
            ]

        else:

            selected_road_ids = edge_ids[
                :SAMPLE_ROAD_COUNT
            ]

        print(
            f"Testing {len(selected_road_ids)} roads..."
        )

        # --------------------------------------------------
        # Create RoadStates
        # --------------------------------------------------

        for road_id in selected_road_ids:

            try:

                road_state = create_road_state(
                    road_id
                )

                simulation_state.roads[road_id] = road_state

            except ValueError as error:

                print(error)

        # --------------------------------------------------
        # Display Initial Roads
        # --------------------------------------------------

        print("\nInitial Road States:")

        for road_id, road in simulation_state.roads.items():

            print(
                f"{road_id} -> "
                f"vehicles={road.vehicle_count}, "
                f"speed={road.current_speed}, "
                f"travel_time={road.travel_time}, "
                f"congestion={road.congestion_level}"
            )

        # --------------------------------------------------
        # Multi-Road State Update
        # --------------------------------------------------

        print("\nMulti-Road State Update:")

        for step in range(5):

            traci.simulationStep()

            simulation_state.simulation_time = (
                traci.simulation.getTime()
            )

            update_road_states(
                simulation_state.roads
            )

            print(
                f"\nStep {step + 1}: "
                f"time={simulation_state.simulation_time}"
            )

            for road_id, road in simulation_state.roads.items():

                print(
                    f"{road_id} -> "
                    f"vehicles={road.vehicle_count}, "
                    f"speed={road.current_speed}, "
                    f"travel_time={road.travel_time}, "
                    f"congestion={road.congestion_level}"
                )

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        print("\nMulti-Road Synchronization Validation:")

        assert len(simulation_state.roads) > 0
        assert len(simulation_state.roads) <= SAMPLE_ROAD_COUNT

        for road_id, road in simulation_state.roads.items():

            assert road.road_id == road_id
            assert road.from_node is not None
            assert road.to_node is not None
            assert road.distance >= 0
            assert road.speed_limit >= 0
            assert road.current_speed >= 0
            assert road.vehicle_count >= 0
            assert road.travel_time >= 0
            assert road.congestion_level != ""

        print(
            "Multi-road synchronization validation successful!"
        )

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()