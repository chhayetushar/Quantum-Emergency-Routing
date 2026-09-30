from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_event_manager import (
    EmergencyEventManager
)


def main():

    # --------------------------------------------------
    # Create Simulation State
    # --------------------------------------------------

    simulation_state = SimulationState(
        simulation_time=10.0
    )

    emergency_manager = EmergencyEventManager(
        simulation_state
    )

    # --------------------------------------------------
    # Create Multiple Emergencies
    # --------------------------------------------------

    emergency_1 = emergency_manager.create_emergency(
        emergency_id="E001",
        emergency_type="ACCIDENT",
        location="175538301#0",
        severity="HIGH"
    )

    # Move simulation time forward
    simulation_state.simulation_time = 20.0

    emergency_2 = emergency_manager.create_emergency(
        emergency_id="E002",
        emergency_type="FIRE",
        location="175538301#2",
        severity="CRITICAL"
    )

    # Move simulation time forward again
    simulation_state.simulation_time = 30.0

    emergency_3 = emergency_manager.create_emergency(
        emergency_id="E003",
        emergency_type="MEDICAL",
        location="175538301#5",
        severity="MEDIUM"
    )

    # --------------------------------------------------
    # Display Emergencies
    # --------------------------------------------------

    print("Created Emergencies:")

    for emergency_id, emergency in (
        simulation_state.emergencies.items()
    ):
        print(
            emergency_id,
            "->",
            emergency
        )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    print("\nMultiple Emergency Validation:")

    assert len(simulation_state.emergencies) == 3

    assert "E001" in simulation_state.emergencies
    assert "E002" in simulation_state.emergencies
    assert "E003" in simulation_state.emergencies

    assert (
        simulation_state.emergencies["E001"].emergency_type
        == "ACCIDENT"
    )

    assert (
        simulation_state.emergencies["E002"].emergency_type
        == "FIRE"
    )

    assert (
        simulation_state.emergencies["E003"].emergency_type
        == "MEDICAL"
    )

    # Validate creation times
    assert (
        simulation_state.emergencies["E001"].creation_time
        == 10.0
    )

    assert (
        simulation_state.emergencies["E002"].creation_time
        == 20.0
    )

    assert (
        simulation_state.emergencies["E003"].creation_time
        == 30.0
    )

    # All new emergencies should initially be waiting
    assert (
        simulation_state.emergencies["E001"].status
        == "WAITING"
    )

    assert (
        simulation_state.emergencies["E002"].status
        == "WAITING"
    )

    assert (
        simulation_state.emergencies["E003"].status
        == "WAITING"
    )

    # No emergency should have a vehicle assigned yet
    assert (
        simulation_state.emergencies["E001"].assigned_vehicle
        is None
    )

    assert (
        simulation_state.emergencies["E002"].assigned_vehicle
        is None
    )

    assert (
        simulation_state.emergencies["E003"].assigned_vehicle
        is None
    )

    print(
        "Multiple emergency validation successful!"
    )


if __name__ == "__main__":
    main()