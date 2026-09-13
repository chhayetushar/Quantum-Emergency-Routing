from Simulation.state.simulation_state import SimulationState
from Simulation.state.emergency_state import EmergencyState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


def test_emergency_assignment_tracking():
    simulation_state = SimulationState()

    # Create a test emergency directly in simulation state
    emergency = EmergencyState(
        emergency_id="E001",
        emergency_type="MEDICAL",
        location="ROAD_001",
        severity="HIGH",
        creation_time=10.0
    )

    simulation_state.emergencies["E001"] = emergency

    # Create manager and register vehicle
    manager = EmergencyVehicleManager(simulation_state)

    vehicle = manager.register_vehicle(
        vehicle_id="ambulance_01",
        vehicle_type="AMBULANCE"
    )

    assert vehicle.status == "AVAILABLE"
    assert vehicle.assigned_emergency is None

    # Assign emergency
    manager.assign_emergency(
        vehicle_id="ambulance_01",
        emergency_id="E001"
    )

    assert vehicle.assigned_emergency == "E001"

    print("Emergency assignment tracking validation successful!")


if __name__ == "__main__":
    test_emergency_assignment_tracking()