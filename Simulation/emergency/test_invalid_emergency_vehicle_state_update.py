from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


def test_invalid_emergency_vehicle_state_update():
    simulation_state = SimulationState()

    manager = EmergencyVehicleManager(simulation_state)

    manager.register_vehicle(
        vehicle_id="ambulance_01",
        vehicle_type="AMBULANCE"
    )

    # Test 1: Negative speed must be rejected
    try:
        manager.update_vehicle_state(
            vehicle_id="ambulance_01",
            current_edge="ROAD_001",
            speed=-5.0,
            position=10.0
        )

        raise AssertionError(
            "Negative vehicle speed was accepted."
        )

    except ValueError as error:
        assert "speed cannot be negative" in str(error)

    # Test 2: Negative position must be rejected
    try:
        manager.update_vehicle_state(
            vehicle_id="ambulance_01",
            current_edge="ROAD_001",
            speed=10.0,
            position=-10.0
        )

        raise AssertionError(
            "Negative vehicle position was accepted."
        )

    except ValueError as error:
        assert "position cannot be negative" in str(error)

    print(
        "Invalid emergency vehicle state update validation successful!"
    )


if __name__ == "__main__":
    test_invalid_emergency_vehicle_state_update()