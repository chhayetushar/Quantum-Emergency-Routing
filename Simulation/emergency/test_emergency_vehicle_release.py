from Simulation.state.simulation_state import SimulationState
from Simulation.state.emergency_state import EmergencyState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


def test_emergency_vehicle_release():
    simulation_state = SimulationState()

    emergency = EmergencyState(
        emergency_id="E001",
        emergency_type="MEDICAL",
        location="ROAD_001",
        severity="HIGH",
        creation_time=10.0
    )

    simulation_state.emergencies["E001"] = emergency

    manager = EmergencyVehicleManager(simulation_state)

    vehicle = manager.register_vehicle(
        vehicle_id="ambulance_01",
        vehicle_type="AMBULANCE"
    )

    manager.assign_emergency(
        vehicle_id="ambulance_01",
        emergency_id="E001"
    )

    manager.update_status(
        vehicle_id="ambulance_01",
        new_status="ASSIGNED"
    )

    manager.update_status(
        vehicle_id="ambulance_01",
        new_status="EN_ROUTE"
    )

    manager.update_status(
        vehicle_id="ambulance_01",
        new_status="AT_SCENE"
    )

    manager.update_status(
        vehicle_id="ambulance_01",
        new_status="RETURNING"
    )

    assert vehicle.status == "RETURNING"
    assert vehicle.assigned_emergency == "E001"

    manager.release_vehicle("ambulance_01")

    assert vehicle.status == "AVAILABLE"
    assert vehicle.assigned_emergency is None

    print("Emergency vehicle release validation successful!")


if __name__ == "__main__":
    test_emergency_vehicle_release()