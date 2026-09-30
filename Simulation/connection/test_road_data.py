from Simulation.connection.sumo_connection import SumoConnection
from Simulation.state.simulation_state import SimulationState
from Simulation.state.road_state import RoadState
from Simulation.traffic.congestion import calculate_congestion_level

import traci


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
SUMO_CONFIG = r"D:\Mini_Project\Quantum-Emergency-Routing\sumo\emergency_simulation.sumocfg"

SAMPLE_ROAD_COUNT = 10


def create_road_state(edge_id: str) -> RoadState:

    # --------------------------------------------------
    # Static Road Properties
    # --------------------------------------------------

    from_node = traci.edge.getFromJunction(edge_id)
    to_node = traci.edge.getToJunction(edge_id)

    lane_count = traci.edge.getLaneNumber(edge_id)

    if lane_count == 0:
        raise ValueError(
            f"Edge {edge_id} has no lanes."
        )

    lane_id = f"{edge_id}_0"

    distance = traci.lane.getLength(lane_id)
    speed_limit = traci.lane.getMaxSpeed(lane_id)

    # --------------------------------------------------
    # Dynamic Road Properties
    # --------------------------------------------------

    vehicle_count = traci.edge.getLastStepVehicleNumber(
        edge_id
    )

    mean_speed = traci.edge.getLastStepMeanSpeed(
        edge_id
    )

    mean_travel_time = traci.edge.getTraveltime(
        edge_id
    )

    # --------------------------------------------------
    # Congestion
    # --------------------------------------------------

    congestion_level = calculate_congestion_level(
        current_speed=mean_speed,
        speed_limit=speed_limit
    )

    # --------------------------------------------------
    # Create RoadState
    # --------------------------------------------------

    return RoadState(
        road_id=edge_id,
        from_node=from_node,
        to_node=to_node,
        distance=distance,
        speed_limit=speed_limit,
        current_speed=mean_speed,
        vehicle_count=vehicle_count,
        travel_time=mean_travel_time,
        congestion_level=congestion_level
    )


def main():

    connection = SumoConnection(
        sumo_binary=SUMO_BINARY,
        config_file=SUMO_CONFIG
    )

    try:

        # --------------------------------------------------
        # Start SUMO
        # --------------------------------------------------

        print("Starting SUMO...")

        connection.start()

        print("SUMO started successfully!")
        print("TraCI connection established.")

        # --------------------------------------------------
        # First Simulation Step
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

        print("\nTotal edges in SUMO:")
        print(len(edge_ids))

        active_road_ids = []

        for edge_id in edge_ids:

            vehicle_count = traci.edge.getLastStepVehicleNumber(
                edge_id
            )

            if vehicle_count > 0:
                active_road_ids.append(edge_id)

        print(
            f"\nFound {len(active_road_ids)} roads "
            f"with active traffic."
        )

        if not active_road_ids:

            print(
                "No active roads found. "
                "Dynamic active-road validation cannot be performed."
            )
            return

        # Select one active road
        edge_id = active_road_ids[0]

        print(f"Selected active road: {edge_id}")

        # --------------------------------------------------
        # Create Initial RoadState
        # --------------------------------------------------

        road_state = create_road_state(edge_id)

        simulation_state.roads[edge_id] = road_state

        print("\nInitial Road State:")
        print(road_state)

        # --------------------------------------------------
        # Dynamic Active-Road Update
        # --------------------------------------------------

        print("\nActive Road Dynamic Update Validation:")

        for step in range(5):

            # Advance SUMO
            traci.simulationStep()

            # Update simulation time
            simulation_state.simulation_time = (
                traci.simulation.getTime()
            )

            # Check if road still has a valid edge
            current_edge_ids = set(
                traci.edge.getIDList()
            )

            assert edge_id in current_edge_ids

            # --------------------------------------------------
            # Read current road data
            # --------------------------------------------------

            vehicle_count = (
                traci.edge.getLastStepVehicleNumber(
                    edge_id
                )
            )

            mean_speed = (
                traci.edge.getLastStepMeanSpeed(
                    edge_id
                )
            )

            mean_travel_time = (
                traci.edge.getTraveltime(
                    edge_id
                )
            )

            congestion_level = (
                calculate_congestion_level(
                    current_speed=mean_speed,
                    speed_limit=road_state.speed_limit
                )
            )

            # --------------------------------------------------
            # Update RoadState
            # --------------------------------------------------

            road_state.vehicle_count = vehicle_count
            road_state.current_speed = mean_speed
            road_state.travel_time = mean_travel_time
            road_state.congestion_level = congestion_level

            # --------------------------------------------------
            # Validate Update
            # --------------------------------------------------

            assert road_state.vehicle_count == vehicle_count
            assert road_state.current_speed == mean_speed
            assert road_state.travel_time == mean_travel_time
            assert road_state.congestion_level == congestion_level

            print(
                f"Step {step + 1}: "
                f"time={simulation_state.simulation_time}, "
                f"vehicles={vehicle_count}, "
                f"speed={mean_speed}, "
                f"travel_time={mean_travel_time}, "
                f"congestion={congestion_level}"
            )

        print(
            "\nActive road dynamic update validation successful!"
        )

        # --------------------------------------------------
        # Final State
        # --------------------------------------------------

        print("\nFinal Road State:")
        print(simulation_state.roads[edge_id])

        print("\nFinal Simulation State:")
        print(simulation_state)

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()