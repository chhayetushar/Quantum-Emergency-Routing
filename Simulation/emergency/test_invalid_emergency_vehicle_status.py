from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


def test_invalid_emergency_vehicle_status_transition():
    simulation_state = SimulationState()

    manager = EmergencyVehicleManager(simulation_state)

    manager.register_vehicle(
        vehicle_id="ambulance_01",
        vehicle_type="AMBULANCE"
    )

    try:
        manager.update_status(
            "ambulance_01",
            "EN_ROUTE"
        )

        raise AssertionError(
            "Invalid status transition was accepted."
        )

    except ValueError as error:
        assert "Invalid status transition" in str(error)

    print(
        "Invalid emergency vehicle status transition validation successful!"
    )


if __name__ == "__main__":
    test_invalid_emergency_vehicle_status_transition()