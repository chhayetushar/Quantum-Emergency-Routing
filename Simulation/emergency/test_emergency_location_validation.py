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

    simulation_state.roads["ROAD_001"] = RoadState(
        road_id="ROAD_001",
        from_node="NODE_A",
        to_node="NODE_B",
        distance=100.0,
        speed_limit=13.89,
        current_speed=13.89,
        vehicle_count=0,
        travel_time=7.2,
        congestion_level="LOW"
    )

    emergency_manager = EmergencyEventManager(
        simulation_state
    )

    # --------------------------------------------------
    # Valid Location
    # --------------------------------------------------

    emergency = emergency_manager.create_emergency(
        emergency_id="E001",
        emergency_type="ACCIDENT",
        location="ROAD_001",
        severity="HIGH"
    )

    print("Valid emergency created:")
    print(emergency)

    # --------------------------------------------------
    # Invalid Location
    # --------------------------------------------------

    print("\nTesting invalid emergency location:")

    try:

        emergency_manager.create_emergency(
            emergency_id="E002",
            emergency_type="FIRE",
            location="INVALID_ROAD",
            severity="CRITICAL"
        )

        raise AssertionError(
            "Invalid emergency location was accepted."
        )

    except ValueError as error:

        print(error)

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    print("\nEmergency Location Validation:")

    assert len(simulation_state.emergencies) == 1

    assert "E001" in simulation_state.emergencies

    assert (
        simulation_state.emergencies["E001"].location
        == "ROAD_001"
    )

    assert "E002" not in simulation_state.emergencies

    print(
        "Emergency location validation successful!"
    )


if __name__ == "__main__":
    main()