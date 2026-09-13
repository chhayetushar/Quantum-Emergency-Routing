from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


def test_emergency_vehicle_state_update():
    simulation_state = SimulationState()

    manager = EmergencyVehicleManager(simulation_state)

    vehicle = manager.register_vehicle(
        vehicle_id="ambulance_01",
        vehicle_type="AMBULANCE"
    )

    manager.update_vehicle_state(
        vehicle_id="ambulance_01",
        current_edge="ROAD_015",
        speed=13.7,
        position=82.4
    )

    assert vehicle.current_edge == "ROAD_015"
    assert vehicle.speed == 13.7
    assert vehicle.position == 82.4

    print("Emergency vehicle state update validation successful!")


if __name__ == "__main__":
    test_emergency_vehicle_state_update()