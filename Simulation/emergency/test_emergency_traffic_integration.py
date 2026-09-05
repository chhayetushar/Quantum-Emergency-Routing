from Simulation.connection.sumo_connection import SumoConnection
from Simulation.state.simulation_state import SimulationState
from Simulation.traffic.traffic_state_manager import (
    TrafficStateManager
)
from Simulation.emergency.emergency_event_manager import (
    EmergencyEventManager
)

import traci


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def main():

    connection = SumoConnection(
        sumo_binary=SUMO_BINARY,
        config_file=SUMO_CONFIG
    )

    try:

        # --------------------------------------------------
        # Start SUMO
        # --------------------------------------------------

        print("Starting SUMO...")

        connection.start()

        print("SUMO started successfully!")
        print("TraCI connection established.")

        # --------------------------------------------------
        # Create Central Simulation State
        # --------------------------------------------------

        simulation_state = SimulationState()

        # --------------------------------------------------
        # Create Managers
        # --------------------------------------------------

        traffic_manager = TrafficStateManager(
            simulation_state
        )

        emergency_manager = EmergencyEventManager(
            simulation_state
        )

        # --------------------------------------------------
        # Advance SUMO and Synchronize Traffic
        # --------------------------------------------------

        traffic_manager.step(
            max_new_roads=10
        )

        print(
            f"\nSimulation time: "
            f"{simulation_state.simulation_time}"
        )

        print(
            f"Known roads: "
            f"{len(simulation_state.roads)}"
        )

        if not simulation_state.roads:

            print(
                "No roads are available in SimulationState."
            )

            return

        # --------------------------------------------------
        # Select a Known Road
        # --------------------------------------------------

        emergency_location = next(
            iter(simulation_state.roads)
        )

        print(
            f"Emergency location: "
            f"{emergency_location}"
        )

        # --------------------------------------------------
        # Create Emergency
        # --------------------------------------------------

        emergency = emergency_manager.create_emergency(
            emergency_id="E001",
            emergency_type="ACCIDENT",
            location=emergency_location,
            severity="HIGH"
        )

        # --------------------------------------------------
        # Display Emergency
        # --------------------------------------------------

        print("\nCreated Emergency:")
        print(emergency)

        print(
            "\nEmergencies stored in SimulationState:"
        )

        for emergency_id, emergency_state in (
            simulation_state.emergencies.items()
        ):

            print(
                emergency_id,
                "->",
                emergency_state
            )

        # --------------------------------------------------
        # Integration Validation
        # --------------------------------------------------

        print(
            "\nEmergency-Traffic Integration Validation:"
        )

        # Emergency location must exist in the
        # centralized road state
        assert (
            emergency.location
            in simulation_state.roads
        )

        # The corresponding road must have the same ID
        road_state = simulation_state.roads[
            emergency.location
        ]

        assert road_state.road_id == emergency.location

        # Emergency must use the current simulation time
        assert (
            emergency.creation_time
            == simulation_state.simulation_time
        )

        # Initial emergency state
        assert emergency.status == "WAITING"
        assert emergency.assigned_vehicle is None

        print(
            "Emergency-traffic integration "
            "validation successful!"
        )

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()