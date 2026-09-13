from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


def test_emergency_vehicle_type_validation():
    simulation_state = SimulationState()

    manager = EmergencyVehicleManager(simulation_state)

    try:
        manager.register_vehicle(
            vehicle_id="vehicle_01",
            vehicle_type="TAXI"
        )

        raise AssertionError(
            "Invalid emergency vehicle type was accepted."
        )

    except ValueError as error:
        assert "Invalid emergency vehicle type" in str(error)

    print("Emergency vehicle type validation successful!")


if __name__ == "__main__":
    test_emergency_vehicle_type_validation()