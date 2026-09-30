import traci

from Simulation.state.road_state import RoadState
from Simulation.traffic.congestion import calculate_congestion_level


def create_road_state(edge_id: str) -> RoadState:
    """
    Read static and dynamic information from SUMO
    and create a RoadState object.
    """

    # --------------------------------------------------
    # Static Road Properties
    # --------------------------------------------------

    from_node = traci.edge.getFromJunction(edge_id)
    to_node = traci.edge.getToJunction(edge_id)

    lane_count = traci.edge.getLaneNumber(edge_id)

    if lane_count <= 0:
        raise ValueError(
            f"Edge {edge_id} has no lanes."
        )

    # Use the first lane for length and speed limit
    lane_id = f"{edge_id}_0"

    distance = traci.lane.getLength(lane_id)
    speed_limit = traci.lane.getMaxSpeed(lane_id)

    # --------------------------------------------------
    # Dynamic Traffic Properties
    # --------------------------------------------------

    vehicle_count = traci.edge.getLastStepVehicleNumber(
        edge_id
    )

    current_speed = traci.edge.getLastStepMeanSpeed(
        edge_id
    )

    travel_time = traci.edge.getTraveltime(
        edge_id
    )

    # --------------------------------------------------
    # Congestion
    # --------------------------------------------------

    congestion_level = calculate_congestion_level(
        current_speed=current_speed,
        speed_limit=speed_limit
    )

    # --------------------------------------------------
    # Create RoadState
    # --------------------------------------------------

    return RoadState(
        road_id=edge_id,
        from_node=from_node,
        to_node=to_node,
        distance=distance,
        speed_limit=speed_limit,
        current_speed=current_speed,
        vehicle_count=vehicle_count,
        travel_time=travel_time,
        congestion_level=congestion_level
    )


def update_road_state(road_state: RoadState) -> None:
    """
    Update the dynamic properties of one existing RoadState.

    Static properties are not changed.
    """

    edge_id = road_state.road_id

    # --------------------------------------------------
    # Read Current Dynamic Data
    # --------------------------------------------------

    vehicle_count = traci.edge.getLastStepVehicleNumber(
        edge_id
    )

    current_speed = traci.edge.getLastStepMeanSpeed(
        edge_id
    )

    travel_time = traci.edge.getTraveltime(
        edge_id
    )

    # --------------------------------------------------
    # Recalculate Congestion
    # --------------------------------------------------

    congestion_level = calculate_congestion_level(
        current_speed=current_speed,
        speed_limit=road_state.speed_limit
    )

    # --------------------------------------------------
    # Update Dynamic Fields
    # --------------------------------------------------

    road_state.vehicle_count = vehicle_count
    road_state.current_speed = current_speed
    road_state.travel_time = travel_time
    road_state.congestion_level = congestion_level


def update_road_states(
    road_states: dict[str, RoadState]
) -> None:
    """
    Update multiple existing RoadState objects.

    Each RoadState is updated using the reusable
    update_road_state() function.
    """

    for road_id, road_state in road_states.items():

        # Ensure the dictionary key matches the RoadState ID
        if road_id != road_state.road_id:
            raise ValueError(
                f"Road ID mismatch: key={road_id}, "
                f"road_state={road_state.road_id}"
            )

        update_road_state(road_state)