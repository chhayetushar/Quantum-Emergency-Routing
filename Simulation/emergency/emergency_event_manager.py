from Simulation.state.emergency_state import EmergencyState
from Simulation.state.simulation_state import SimulationState


class EmergencyEventManager:
    """
    Manages emergency events for the simulation.
    """

    VALID_EMERGENCY_TYPES = {
        "ACCIDENT",
        "FIRE",
        "MEDICAL"
    }

    VALID_SEVERITIES = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    }

    SEVERITY_PRIORITY = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }

    VALID_STATUS_TRANSITIONS = {
        "WAITING": {"ASSIGNED"},
        "ASSIGNED": {"IN_PROGRESS"},
        "IN_PROGRESS": {"COMPLETED"},
        "COMPLETED": set()
    }

    def __init__(
        self,
        simulation_state: SimulationState
    ):
        self.simulation_state = simulation_state

    def create_emergency(
        self,
        emergency_id: str,
        emergency_type: str,
        location: str,
        severity: str
    ) -> EmergencyState:
        """
        Create a new emergency event and store it
        in SimulationState.
        """

        # --------------------------------------------------
        # Validate Emergency ID
        # --------------------------------------------------

        if emergency_id in self.simulation_state.emergencies:
            raise ValueError(
                f"Emergency ID '{emergency_id}' already exists."
            )

        # --------------------------------------------------
        # Validate Emergency Type
        # --------------------------------------------------

        if emergency_type not in self.VALID_EMERGENCY_TYPES:
            raise ValueError(
                f"Invalid emergency type: '{emergency_type}'. "
                f"Valid types are: "
                f"{sorted(self.VALID_EMERGENCY_TYPES)}"
            )

        # --------------------------------------------------
        # Validate Severity
        # --------------------------------------------------

        if severity not in self.VALID_SEVERITIES:
            raise ValueError(
                f"Invalid severity: '{severity}'. "
                f"Valid severities are: "
                f"{sorted(self.VALID_SEVERITIES)}"
            )

        # --------------------------------------------------
        # Validate Emergency Location
        # --------------------------------------------------

        if location not in self.simulation_state.roads:
            raise ValueError(
                f"Invalid emergency location: '{location}'. "
                f"The location must be a known road in "
                f"SimulationState."
            )

        # --------------------------------------------------
        # Create Emergency
        # --------------------------------------------------

        creation_time = (
            self.simulation_state.simulation_time
        )

        emergency = EmergencyState(
            emergency_id=emergency_id,
            emergency_type=emergency_type,
            location=location,
            severity=severity,
            creation_time=creation_time,
            status="WAITING"
        )

        # --------------------------------------------------
        # Store Emergency
        # --------------------------------------------------

        self.simulation_state.emergencies[
            emergency_id
        ] = emergency

        return emergency

    def update_status(
        self,
        emergency_id: str,
        new_status: str
    ) -> EmergencyState:
        """
        Change the status of an existing emergency.

        Only valid status transitions are allowed.
        """

        # --------------------------------------------------
        # Validate Emergency ID
        # --------------------------------------------------

        if emergency_id not in self.simulation_state.emergencies:
            raise ValueError(
                f"Emergency ID '{emergency_id}' does not exist."
            )

        emergency = self.simulation_state.emergencies[
            emergency_id
        ]

        current_status = emergency.status

        # --------------------------------------------------
        # Validate New Status
        # --------------------------------------------------

        if new_status not in self.VALID_STATUS_TRANSITIONS:
            raise ValueError(
                f"Invalid emergency status: '{new_status}'."
            )

        # --------------------------------------------------
        # Validate Status Transition
        # --------------------------------------------------

        allowed_statuses = self.VALID_STATUS_TRANSITIONS[
            current_status
        ]

        if new_status not in allowed_statuses:
            raise ValueError(
                f"Invalid status transition: "
                f"{current_status} -> {new_status}"
            )

        # --------------------------------------------------
        # Update Status
        # --------------------------------------------------

        emergency.status = new_status

        return emergency

    def get_emergency_priority(
        self,
        emergency_id: str
    ) -> int:
        """
        Return the numerical priority of an existing
        emergency based on its severity.
        """

        # --------------------------------------------------
        # Validate Emergency ID
        # --------------------------------------------------

        if emergency_id not in self.simulation_state.emergencies:
            raise ValueError(
                f"Emergency ID '{emergency_id}' does not exist."
            )

        # --------------------------------------------------
        # Get Emergency
        # --------------------------------------------------

        emergency = self.simulation_state.emergencies[
            emergency_id
        ]

        # --------------------------------------------------
        # Return Priority
        # --------------------------------------------------

        return self.SEVERITY_PRIORITY[
            emergency.severity
        ]

    def get_prioritized_emergencies(
        self
    ) -> list[EmergencyState]:
        """
        Return waiting emergencies ordered by priority.

        Higher severity priority comes first.
        If two emergencies have the same priority,
        the earlier-created emergency comes first.
        """

        waiting_emergencies = [
            emergency
            for emergency
            in self.simulation_state.emergencies.values()
            if emergency.status == "WAITING"
        ]

        waiting_emergencies.sort(
            key=lambda emergency: (
                -self.SEVERITY_PRIORITY[emergency.severity],
                emergency.creation_time
            )
        )

        return waiting_emergencies