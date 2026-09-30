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
        # Advance Simulation
        # --------------------------------------------------

        traci.simulationStep()

        # --------------------------------------------------
        # Create Simulation State
        # --------------------------------------------------

        simulation_state = SimulationState(
            simulation_time=traci.simulation.getTime()
        )

        # --------------------------------------------------
        # Create Emergency Event Manager
        # --------------------------------------------------

        emergency_manager = EmergencyEventManager(
            simulation_state
        )

        # --------------------------------------------------
        # Get Valid SUMO Roads
        # --------------------------------------------------

        edge_ids = traci.edge.getIDList()

        print("\nTotal SUMO roads:")
        print(len(edge_ids))

        if not edge_ids:

            print("No SUMO roads available.")
            return

        # Select one valid road
        emergency_location = edge_ids[0]

        print(
            f"\nSelected emergency location: "
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

        print("\nSUMO Emergency Location Validation:")

        assert emergency.location in edge_ids

        assert emergency.emergency_id == "E001"
        assert emergency.emergency_type == "ACCIDENT"
        assert emergency.severity == "HIGH"
        assert emergency.status == "WAITING"
        assert emergency.assigned_vehicle is None

        assert (
            emergency.creation_time
            == simulation_state.simulation_time
        )

        print(
            "SUMO emergency location validation successful!"
        )

    finally:

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()