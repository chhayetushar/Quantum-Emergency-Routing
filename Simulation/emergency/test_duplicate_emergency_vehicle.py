from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


def test_duplicate_emergency_vehicle():
    simulation_state = SimulationState()

    manager = EmergencyVehicleManager(simulation_state)

    manager.register_vehicle(
        vehicle_id="ambulance_01",
        vehicle_type="AMBULANCE"
    )

    try:
        manager.register_vehicle(
            vehicle_id="ambulance_01",
            vehicle_type="AMBULANCE"
        )

        raise AssertionError(
            "Duplicate emergency vehicle was accepted."
        )

    except ValueError as error:
        assert "already exists" in str(error)

    print("Duplicate emergency vehicle protection validation successful!")


if __name__ == "__main__":
    test_duplicate_emergency_vehicle()