from Simulation.state.simulation_state import SimulationState
from Simulation.state.road_state import RoadState
from Simulation.emergency.emergency_event_manager import (
    EmergencyEventManager
)


def main():

    # --------------------------------------------------
    # Create Simulation State
    # --------------------------------------------------

    simulation_state = SimulationState(
        simulation_time=10.0
    )

    # --------------------------------------------------
    # Add Known Roads
    # --------------------------------------------------

    for road_id in [
        "ROAD_001",
        "ROAD_002",
        "ROAD_003",
        "ROAD_004"
    ]:

        simulation_state.roads[road_id] = RoadState(
            road_id=road_id,
            from_node="NODE_A",
            to_node="NODE_B",
            distance=100.0,
            speed_limit=13.89,
            current_speed=13.89,
            vehicle_count=0,
            travel_time=7.2,
            congestion_level="LOW"
        )

    # --------------------------------------------------
    # Create Emergency Manager
    # --------------------------------------------------

    emergency_manager = EmergencyEventManager(
        simulation_state
    )

    # --------------------------------------------------
    # Create Emergencies
    # --------------------------------------------------

    emergency_manager.create_emergency(
        emergency_id="E001",
        emergency_type="ACCIDENT",
        location="ROAD_001",
        severity="LOW"
    )

    simulation_state.simulation_time = 20.0

    emergency_manager.create_emergency(
        emergency_id="E002",
        emergency_type="FIRE",
        location="ROAD_002",
        severity="CRITICAL"
    )

    simulation_state.simulation_time = 15.0

    emergency_manager.create_emergency(
        emergency_id="E003",
        emergency_type="MEDICAL",
        location="ROAD_003",
        severity="HIGH"
    )

    simulation_state.simulation_time = 12.0

    emergency_manager.create_emergency(
        emergency_id="E004",
        emergency_type="ACCIDENT",
        location="ROAD_004",
        severity="HIGH"
    )

    # --------------------------------------------------
    # Get Prioritized Emergencies
    # --------------------------------------------------

    prioritized_emergencies = (
        emergency_manager.get_prioritized_emergencies()
    )

    print("Priority-Ordered Emergencies:")

    for emergency in prioritized_emergencies:

        priority = (
            emergency_manager.get_emergency_priority(
                emergency.emergency_id
            )
        )

        print(
            f"{emergency.emergency_id} -> "
            f"severity={emergency.severity}, "
            f"priority={priority}, "
            f"creation_time={emergency.creation_time}"
        )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    print("\nEmergency Priority Ordering Validation:")

    assert len(prioritized_emergencies) == 4

    # Highest priority first
    assert prioritized_emergencies[0].emergency_id == "E002"

    # HIGH priority emergencies next.
    # E004 was created earlier than E003.
    assert prioritized_emergencies[1].emergency_id == "E004"
    assert prioritized_emergencies[2].emergency_id == "E003"

    # LOW priority last
    assert prioritized_emergencies[3].emergency_id == "E001"

    print(
        "Emergency priority ordering validation successful!"
    )


if __name__ == "__main__":
    main()