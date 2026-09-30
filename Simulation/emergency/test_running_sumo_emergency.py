from Simulation.connection.sumo_connection import SumoConnection
from Simulation.state.simulation_state import SimulationState
from Simulation.emergency.emergency_event_manager import (
    EmergencyEventManager
)

import traci


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
SUMO_CONFIG = r"D:\Mini_Project\Quantum-Emergency-Routing\sumo\emergency_simulation.sumocfg"


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
        # Create Simulation State
        # --------------------------------------------------

        simulation_state = SimulationState()

        emergency_manager = EmergencyEventManager(
            simulation_state
        )

        # --------------------------------------------------
        # Advance SUMO
        # --------------------------------------------------

        traci.simulationStep()

        simulation_state.simulation_time = (
            traci.simulation.getTime()
        )

        print(
            f"\nSimulation time: "
            f"{simulation_state.simulation_time}"
        )

        # --------------------------------------------------
        # Get Real SUMO Roads
        # --------------------------------------------------

        edge_ids = traci.edge.getIDList()

        print(
            f"Total SUMO roads: {len(edge_ids)}"
        )

        if not edge_ids:

            print("No roads available in SUMO.")
            return

        # Use a real SUMO edge as the emergency location
        emergency_location = edge_ids[0]

        print(
            f"Emergency location: "
            f"{emergency_location}"
        )

        # --------------------------------------------------
        # Create Emergency During Simulation
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

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        print(
            "\nRunning SUMO Emergency Timing Validation:"
        )

        # Emergency creation time must equal the
        # current simulation time
        assert (
            emergency.creation_time
            == simulation_state.simulation_time
        )

        # Emergency location must be a real SUMO edge
        assert emergency.location in edge_ids

        # Initial status
        assert emergency.status == "WAITING"

        # No vehicle assigned yet
        assert emergency.assigned_vehicle is None

        # Emergency must be stored
        assert (
            emergency.emergency_id
            in simulation_state.emergencies
        )

        print(
            "Running SUMO emergency timing "
            "validation successful!"
        )

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()