from Simulation.state.simulation_state import SimulationState
from Simulation.state.emergency_state import EmergencyState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


def test_unavailable_vehicle_assignment():
    simulation_state = SimulationState()

    emergency_1 = EmergencyState(
        emergency_id="E001",
        emergency_type="MEDICAL",
        location="ROAD_001",
        severity="HIGH",
        creation_time=10.0
    )

    emergency_2 = EmergencyState(
        emergency_id="E002",
        emergency_type="FIRE",
        location="ROAD_002",
        severity="CRITICAL",
        creation_time=20.0
    )

    simulation_state.emergencies["E001"] = emergency_1
    simulation_state.emergencies["E002"] = emergency_2

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

    try:
        manager.assign_emergency(
            vehicle_id="ambulance_01",
            emergency_id="E002"
        )

        raise AssertionError(
            "Unavailable emergency vehicle was assigned another emergency."
        )

    except ValueError as error:
        assert "not AVAILABLE" in str(error)

    print(
        "Unavailable emergency vehicle assignment validation successful!"
    )


if __name__ == "__main__":
    test_unavailable_vehicle_assignment()