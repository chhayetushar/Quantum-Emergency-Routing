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
    # Create First Emergency
    # --------------------------------------------------

    first_emergency = emergency_manager.create_emergency(
        emergency_id="E001",
        emergency_type="ACCIDENT",
        location="175538301#0",
        severity="HIGH"
    )

    print("First emergency created:")
    print(first_emergency)

    # --------------------------------------------------
    # Try to Create Duplicate
    # --------------------------------------------------

    try:

        emergency_manager.create_emergency(
            emergency_id="E001",
            emergency_type="FIRE",
            location="175538301#2",
            severity="CRITICAL"
        )

        # If no exception occurs, validation fails
        raise AssertionError(
            "Duplicate emergency ID was not rejected."
        )

    except ValueError as error:

        print("\nDuplicate emergency correctly rejected:")
        print(error)

    # --------------------------------------------------
    # Validate Original Emergency
    # --------------------------------------------------

    print("\nDuplicate Emergency Validation:")

    assert len(simulation_state.emergencies) == 1

    assert (
        simulation_state.emergencies["E001"]
        == first_emergency
    )

    assert (
        simulation_state.emergencies["E001"].emergency_type
        == "ACCIDENT"
    )

    print(
        "Duplicate emergency ID validation successful!"
    )


if __name__ == "__main__":
    main()