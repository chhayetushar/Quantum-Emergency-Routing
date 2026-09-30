from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


def test_emergency_vehicle_status_lifecycle():
    simulation_state = SimulationState()

    manager = EmergencyVehicleManager(simulation_state)

    vehicle = manager.register_vehicle(
        vehicle_id="ambulance_01",
        vehicle_type="AMBULANCE"
    )

    assert vehicle.status == "AVAILABLE"

    manager.update_status("ambulance_01", "ASSIGNED")
    assert vehicle.status == "ASSIGNED"

    manager.update_status("ambulance_01", "EN_ROUTE")
    assert vehicle.status == "EN_ROUTE"

    manager.update_status("ambulance_01", "AT_SCENE")
    assert vehicle.status == "AT_SCENE"

    manager.update_status("ambulance_01", "RETURNING")
    assert vehicle.status == "RETURNING"

    manager.update_status("ambulance_01", "AVAILABLE")
    assert vehicle.status == "AVAILABLE"

    print("Emergency vehicle status lifecycle validation successful!")


if __name__ == "__main__":
    test_emergency_vehicle_status_lifecycle()