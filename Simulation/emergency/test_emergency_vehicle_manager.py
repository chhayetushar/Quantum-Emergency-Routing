from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_vehicle_manager import EmergencyVehicleManager


def test_emergency_vehicle_registration():
    simulation_state = SimulationState()

    manager = EmergencyVehicleManager(simulation_state)

    vehicle = manager.register_vehicle(
        vehicle_id="ambulance_01",
        vehicle_type="AMBULANCE"
    )

    assert vehicle.vehicle_id == "ambulance_01"
    assert vehicle.vehicle_type == "AMBULANCE"
    assert vehicle.status == "AVAILABLE"
    assert vehicle.assigned_emergency is None

    assert "ambulance_01" in simulation_state.emergency_vehicles

    assert (
        simulation_state.emergency_vehicles["ambulance_01"]
        is vehicle
    )

    print("Emergency vehicle registration validation successful!")


if __name__ == "__main__":
    test_emergency_vehicle_registration()