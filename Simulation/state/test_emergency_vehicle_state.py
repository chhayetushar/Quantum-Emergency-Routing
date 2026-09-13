from Simulation.state.emergency_vehicle_state import EmergencyVehicleState


def test_emergency_vehicle_state():
    vehicle = EmergencyVehicleState(
        vehicle_id="ambulance_01",
        vehicle_type="AMBULANCE",
        current_edge="ROAD_001",
        speed=12.5,
        position=45.0,
        status="AVAILABLE",
        assigned_emergency=None
    )

    assert vehicle.vehicle_id == "ambulance_01"
    assert vehicle.vehicle_type == "AMBULANCE"
    assert vehicle.current_edge == "ROAD_001"
    assert vehicle.speed == 12.5
    assert vehicle.position == 45.0
    assert vehicle.status == "AVAILABLE"
    assert vehicle.assigned_emergency is None

    print("Emergency vehicle state validation successful!")


if __name__ == "__main__":
    test_emergency_vehicle_state()