from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_event_manager import (
    EmergencyEventManager
)


def main():

    simulation_state = SimulationState(
        simulation_time=10.0
    )

    emergency_manager = EmergencyEventManager(
        simulation_state
    )

    # --------------------------------------------------
    # Valid Emergency
    # --------------------------------------------------

    valid_emergency = emergency_manager.create_emergency(
        emergency_id="E001",
        emergency_type="ACCIDENT",
        location="175538301#0",
        severity="HIGH"
    )

    print("Valid emergency created:")
    print(valid_emergency)

    # --------------------------------------------------
    # Invalid Emergency Type
    # --------------------------------------------------

    print("\nTesting invalid emergency type:")

    try:

        emergency_manager.create_emergency(
            emergency_id="E002",
            emergency_type="ROBBERY",
            location="175538301#2",
            severity="HIGH"
        )

        raise AssertionError(
            "Invalid emergency type was accepted."
        )

    except ValueError as error:

        print(error)

    # --------------------------------------------------
    # Invalid Severity
    # --------------------------------------------------

    print("\nTesting invalid severity:")

    try:

        emergency_manager.create_emergency(
            emergency_id="E003",
            emergency_type="FIRE",
            location="175538301#5",
            severity="EXTREME"
        )

        raise AssertionError(
            "Invalid severity was accepted."
        )

    except ValueError as error:

        print(error)

    # --------------------------------------------------
    # Final Validation
    # --------------------------------------------------

    print("\nEmergency Type and Severity Validation:")

    assert len(simulation_state.emergencies) == 1

    assert (
        simulation_state.emergencies["E001"]
        == valid_emergency
    )

    assert (
        valid_emergency.emergency_type
        in EmergencyEventManager.VALID_EMERGENCY_TYPES
    )

    assert (
        valid_emergency.severity
        in EmergencyEventManager.VALID_SEVERITIES
    )

    print(
        "Emergency type and severity validation successful!"
    )


if __name__ == "__main__":
    main()