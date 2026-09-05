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

    emergency_manager.create_emergency(
        emergency_id="E002",
        emergency_type="FIRE",
        location="ROAD_002",
        severity="MEDIUM"
    )

    emergency_manager.create_emergency(
        emergency_id="E003",
        emergency_type="MEDICAL",
        location="ROAD_003",
        severity="HIGH"
    )

    emergency_manager.create_emergency(
        emergency_id="E004",
        emergency_type="ACCIDENT",
        location="ROAD_004",
        severity="CRITICAL"
    )

    # --------------------------------------------------
    # Display Priorities
    # --------------------------------------------------

    print("Emergency Priorities:")

    for emergency_id, emergency in (
        simulation_state.emergencies.items()
    ):

        priority = (
            emergency_manager.get_emergency_priority(
                emergency_id
            )
        )

        print(
            f"{emergency_id} -> "
            f"severity={emergency.severity}, "
            f"priority={priority}"
        )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    print("\nEmergency Priority Validation:")

    assert (
        emergency_manager.get_emergency_priority("E001")
        == 1
    )

    assert (
        emergency_manager.get_emergency_priority("E002")
        == 2
    )

    assert (
        emergency_manager.get_emergency_priority("E003")
        == 3
    )

    assert (
        emergency_manager.get_emergency_priority("E004")
        == 4
    )

    print(
        "Emergency priority validation successful!"
    )


if __name__ == "__main__":
    main()