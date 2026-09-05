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
    # Create Emergency
    # --------------------------------------------------

    emergency = emergency_manager.create_emergency(
        emergency_id="E001",
        emergency_type="ACCIDENT",
        location="175538301#0",
        severity="HIGH"
    )

    print("Initial Emergency:")
    print(emergency)

    # --------------------------------------------------
    # WAITING -> ASSIGNED
    # --------------------------------------------------

    emergency_manager.update_status(
        emergency_id="E001",
        new_status="ASSIGNED"
    )

    print("\nAfter assignment:")
    print(emergency)

    # --------------------------------------------------
    # ASSIGNED -> IN_PROGRESS
    # --------------------------------------------------

    emergency_manager.update_status(
        emergency_id="E001",
        new_status="IN_PROGRESS"
    )

    print("\nAfter starting response:")
    print(emergency)

    # --------------------------------------------------
    # IN_PROGRESS -> COMPLETED
    # --------------------------------------------------

    emergency_manager.update_status(
        emergency_id="E001",
        new_status="COMPLETED"
    )

    print("\nAfter completion:")
    print(emergency)

    # --------------------------------------------------
    # Test Invalid Transition
    # --------------------------------------------------

    print("\nTesting invalid transition:")

    try:

        emergency_manager.update_status(
            emergency_id="E001",
            new_status="WAITING"
        )

        raise AssertionError(
            "Invalid status transition was accepted."
        )

    except ValueError as error:

        print(error)

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    print("\nEmergency Status Lifecycle Validation:")

    assert emergency.status == "COMPLETED"

    assert (
        simulation_state.emergencies["E001"].status
        == "COMPLETED"
    )

    print(
        "Emergency status lifecycle validation successful!"
    )


if __name__ == "__main__":
    main()