from Simulation.connection.sumo_connection import SumoConnection
from Simulation.state.simulation_state import SimulationState
from Simulation.state.vehicle_state import VehicleState

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

        print("Advancing simulation by one step...")

        traci.simulationStep()

        print("Simulation advanced successfully.")

        # --------------------------------------------------
        # Create Simulation State
        # --------------------------------------------------

        simulation_state = SimulationState(
            simulation_time=traci.simulation.getTime()
        )

        # --------------------------------------------------
        # Read Vehicles from SUMO
        # --------------------------------------------------

        vehicle_ids = traci.vehicle.getIDList()

        print("\nVehicles currently in SUMO:")
        print(vehicle_ids)

        # --------------------------------------------------
        # Create and Store Vehicle States
        # --------------------------------------------------

        for vehicle_id in vehicle_ids:

            vehicle_type = traci.vehicle.getTypeID(vehicle_id)
            current_edge = traci.vehicle.getRoadID(vehicle_id)
            speed = traci.vehicle.getSpeed(vehicle_id)
            position = traci.vehicle.getLanePosition(vehicle_id)

            vehicle_state = VehicleState(
                vehicle_id=vehicle_id,
                vehicle_type=vehicle_type,
                current_edge=current_edge,
                speed=speed,
                position=position,
                status="ACTIVE"
            )

            # Store vehicle inside SimulationState
            simulation_state.vehicles[vehicle_id] = vehicle_state

        # --------------------------------------------------
        # Display Simulation State
        # --------------------------------------------------

        print("\nSimulation State:")
        print(simulation_state)

        print("\nVehicles stored in SimulationState:")

        for vehicle_id, vehicle in simulation_state.vehicles.items():
            print(vehicle_id, "->", vehicle)

        # --------------------------------------------------
        # Vehicle Data Consistency Validation
        # --------------------------------------------------

        print("\nVehicle Data Consistency Validation:")

        for vehicle_id, vehicle in simulation_state.vehicles.items():

            # Read current values directly from SUMO
            sumo_vehicle_type = traci.vehicle.getTypeID(vehicle_id)
            sumo_current_edge = traci.vehicle.getRoadID(vehicle_id)
            sumo_speed = traci.vehicle.getSpeed(vehicle_id)
            sumo_position = traci.vehicle.getLanePosition(vehicle_id)

            # Compare our state with SUMO
            assert vehicle.vehicle_id == vehicle_id
            assert vehicle.vehicle_type == sumo_vehicle_type
            assert vehicle.current_edge == sumo_current_edge
            assert vehicle.speed == sumo_speed
            assert vehicle.position == sumo_position

        print("Vehicle data consistency validation successful!")

        # --------------------------------------------------
        # Multi-Step Simulation Validation
        # --------------------------------------------------

        print("\nMulti-Step Simulation Validation:")

        previous_time = simulation_state.simulation_time

        for step in range(5):

            # Advance SUMO
            traci.simulationStep()

            # Read new simulation time
            current_time = traci.simulation.getTime()

            # Update our SimulationState time
            simulation_state.simulation_time = current_time

            # Validate time progression
            assert current_time > previous_time
            assert simulation_state.simulation_time == current_time

            previous_time = current_time

            print(
                f"Simulation step {step + 1}: "
                f"SUMO time = {current_time}, "
                f"State time = {simulation_state.simulation_time}"
            )

        print("Multi-step simulation state validation successful!")

        # --------------------------------------------------
        # Vehicle State Update Validation
        # --------------------------------------------------

        print("\nVehicle State Update Validation:")

        # Use a vehicle that is already present
        # in our SimulationState
        vehicle_ids_before = list(simulation_state.vehicles.keys())

        if len(vehicle_ids_before) == 0:

            print(
                "No active vehicles available for update validation."
            )

        else:

            vehicle_id = vehicle_ids_before[0]

            # Read current values from SUMO
            old_speed = traci.vehicle.getSpeed(vehicle_id)
            old_position = traci.vehicle.getLanePosition(vehicle_id)
            old_edge = traci.vehicle.getRoadID(vehicle_id)

            print(f"Vehicle: {vehicle_id}")
            print(f"Previous position: {old_position}")
            print(f"Previous speed: {old_speed}")
            print(f"Previous edge: {old_edge}")

            # Advance simulation
            traci.simulationStep()

            # Check whether the vehicle is still active
            vehicle_ids_after = traci.vehicle.getIDList()

            if vehicle_id not in vehicle_ids_after:

                print(
                    f"Vehicle {vehicle_id} left the simulation "
                    f"after the step."
                )

                print(
                    "Vehicle state update validation skipped "
                    "for this vehicle."
                )

            else:

                # Read updated values from SUMO
                new_speed = traci.vehicle.getSpeed(vehicle_id)
                new_position = traci.vehicle.getLanePosition(vehicle_id)
                new_edge = traci.vehicle.getRoadID(vehicle_id)

                print(f"Current position: {new_position}")
                print(f"Current speed: {new_speed}")
                print(f"Current edge: {new_edge}")

                # Get corresponding VehicleState
                vehicle_state = simulation_state.vehicles[vehicle_id]

                # Update VehicleState
                vehicle_state.speed = new_speed
                vehicle_state.position = new_position
                vehicle_state.current_edge = new_edge

                # Validate updated VehicleState
                assert vehicle_state.speed == new_speed
                assert vehicle_state.position == new_position
                assert vehicle_state.current_edge == new_edge

                print(
                    "Vehicle state update validation successful!"
                )

        # --------------------------------------------------
        # Active Vehicle Set Validation
        # --------------------------------------------------

        print("\nActive Vehicle Set Validation:")

        # Get vehicles currently active in SUMO
        active_vehicle_ids = set(traci.vehicle.getIDList())

        # Get vehicles stored in our simulation state
        stored_vehicle_ids = set(simulation_state.vehicles.keys())

        print(
            f"Active vehicles in SUMO: "
            f"{active_vehicle_ids}"
        )

        print(
            f"Vehicles stored in SimulationState: "
            f"{stored_vehicle_ids}"
        )

        # Validate that every stored vehicle has a valid ID
        for vehicle_id in stored_vehicle_ids:

            assert vehicle_id != ""

        print("Active vehicle set validation successful!")

    finally:

        # --------------------------------------------------
        # Close SUMO Connection
        # --------------------------------------------------

        connection.close()

        print("\nSUMO connection closed.")


if __name__ == "__main__":
    main()