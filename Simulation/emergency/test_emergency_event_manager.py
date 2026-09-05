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

    # --------------------------------------------------
    # Create Emergency Manager
    # --------------------------------------------------

    emergency_manager = EmergencyEventManager(
        simulation_state
    )

    # --------------------------------------------------
    # Create Emergency
    # --------------------------------------------------

    emergency = emergency_manager.create_emergency(
        emergency_id="E001",
        emergency_type="ACCIDENT",
        location="175538301#0",
        severity="HIGH"
    )

    # --------------------------------------------------
    # Display Emergency
    # --------------------------------------------------

    print("Created Emergency:")
    print(emergency)

    print("\nEmergencies stored in SimulationState:")

    for emergency_id, emergency_state in (
        simulation_state.emergencies.items()
    ):
        print(
            emergency_id,
            "->",
            emergency_state
        )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    print("\nEmergency Event Validation:")

    assert emergency.emergency_id == "E001"
    assert emergency.emergency_type == "ACCIDENT"
    assert emergency.location == "175538301#0"
    assert emergency.severity == "HIGH"
    assert emergency.creation_time == 10.0
    assert emergency.status == "WAITING"
    assert emergency.assigned_vehicle is None

    assert "E001" in simulation_state.emergencies

    print(
        "Emergency event validation successful!"
    )


if __name__ == "__main__":
    main()