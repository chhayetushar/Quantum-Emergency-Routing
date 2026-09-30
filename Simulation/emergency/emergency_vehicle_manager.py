import traci
from Simulation.state.emergency_vehicle_state import EmergencyVehicleState
from Simulation.state.simulation_state import SimulationState

class EmergencyVehicleManager:
    """
    Manages emergency vehicle states inside the simulation.
    """

    VALID_VEHICLE_TYPES = {
        "AMBULANCE",
        "POLICE",
        "FIRETRUCK"
    }

    VALID_STATUS_TRANSITIONS = {
        "AVAILABLE": {"ASSIGNED"},
        "ASSIGNED": {"EN_ROUTE"},
        "EN_ROUTE": {"AT_SCENE"},
        "AT_SCENE": {"RETURNING"},
        "RETURNING": {"AVAILABLE"}
    }

    def __init__(self, simulation_state: SimulationState):
        self.simulation_state = simulation_state

    def register_vehicle(
        self,
        vehicle_id: str,
        vehicle_type: str
    ) -> EmergencyVehicleState:

        if vehicle_id in self.simulation_state.emergency_vehicles:
            raise ValueError(
                f"Emergency vehicle '{vehicle_id}' already exists."
            )

        if vehicle_type not in self.VALID_VEHICLE_TYPES:
            raise ValueError(
                f"Invalid emergency vehicle type: {vehicle_type}"
            )

        vehicle = EmergencyVehicleState(
            vehicle_id=vehicle_id,
            vehicle_type=vehicle_type
        )

        self.simulation_state.emergency_vehicles[vehicle_id] = vehicle

        return vehicle

    def update_status(
        self,
        vehicle_id: str,
        new_status: str
    ) -> EmergencyVehicleState:

        if vehicle_id not in self.simulation_state.emergency_vehicles:
            raise ValueError(
                f"Emergency vehicle '{vehicle_id}' does not exist."
            )

        vehicle = self.simulation_state.emergency_vehicles[vehicle_id]

        if new_status not in self.VALID_STATUS_TRANSITIONS:
            raise ValueError(
                f"Invalid emergency vehicle status: {new_status}"
            )

        current_status = vehicle.status
        allowed_statuses = self.VALID_STATUS_TRANSITIONS[current_status]

        if new_status not in allowed_statuses:
            raise ValueError(
                f"Invalid status transition: "
                f"{current_status} -> {new_status}"
            )

        vehicle.status = new_status

        return vehicle

    def assign_emergency(
        self,
        vehicle_id: str,
        emergency_id: str
    ) -> EmergencyVehicleState:

        if vehicle_id not in self.simulation_state.emergency_vehicles:
            raise ValueError(
                f"Emergency vehicle '{vehicle_id}' does not exist."
            )

        if emergency_id not in self.simulation_state.emergencies:
            raise ValueError(
                f"Emergency '{emergency_id}' does not exist."
            )

        vehicle = self.simulation_state.emergency_vehicles[vehicle_id]

        if vehicle.status != "AVAILABLE":
            raise ValueError(
                f"Emergency vehicle '{vehicle_id}' is not AVAILABLE."
            )

        vehicle.assigned_emergency = emergency_id

        return vehicle

    def release_vehicle(
        self,
        vehicle_id: str
    ) -> EmergencyVehicleState:

        if vehicle_id not in self.simulation_state.emergency_vehicles:
            raise ValueError(
                f"Emergency vehicle '{vehicle_id}' does not exist."
            )

        vehicle = self.simulation_state.emergency_vehicles[vehicle_id]

        if vehicle.status != "RETURNING":
            raise ValueError(
                f"Emergency vehicle '{vehicle_id}' must be RETURNING "
                f"before it can be released."
            )

        vehicle.status = "AVAILABLE"
        vehicle.assigned_emergency = None

        return vehicle

    def update_vehicle_state(
        self,
        vehicle_id: str,
        current_edge: str,
        speed: float,
        position: float
    ) -> EmergencyVehicleState:

        if vehicle_id not in self.simulation_state.emergency_vehicles:
            raise ValueError(
                f"Emergency vehicle '{vehicle_id}' does not exist."
            )

        if speed < 0:
            raise ValueError(
                "Vehicle speed cannot be negative."
            )

        if position < 0:
            raise ValueError(
                "Vehicle position cannot be negative."
            )

        vehicle = self.simulation_state.emergency_vehicles[vehicle_id]

        vehicle.current_edge = current_edge
        vehicle.speed = speed
        vehicle.position = position

        return vehicle

    def synchronize_with_sumo(self) -> list[str]:

        emergency_vehicle_ids = []

        active_vehicle_ids = traci.vehicle.getIDList()

        for vehicle_id in active_vehicle_ids:

            vehicle_type = traci.vehicle.getTypeID(vehicle_id)

            normalized_type = vehicle_type.upper()

            if normalized_type not in self.VALID_VEHICLE_TYPES:
                continue

            current_edge = traci.vehicle.getRoadID(vehicle_id)
            speed = traci.vehicle.getSpeed(vehicle_id)
            position = traci.vehicle.getLanePosition(vehicle_id)

            emergency_vehicle_ids.append(vehicle_id)

            if vehicle_id not in self.simulation_state.emergency_vehicles:

                self.register_vehicle(
                    vehicle_id=vehicle_id,
                    vehicle_type=normalized_type
                )

            self.update_vehicle_state(
                vehicle_id=vehicle_id,
                current_edge=current_edge,
                speed=speed,
                position=position
            )

        return emergency_vehicle_ids