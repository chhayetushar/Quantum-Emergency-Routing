import traci


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


EMERGENCY_TYPES = {
    "ambulance",
    "police",
    "firetruck"
}


def test_real_sumo_emergency_vehicle():

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    found_emergency_vehicle = False

    try:
        for step in range(300):

            traci.simulationStep()

            current_time = traci.simulation.getTime()

            vehicle_ids = traci.vehicle.getIDList()

            for vehicle_id in vehicle_ids:

                vehicle_type = traci.vehicle.getTypeID(
                    vehicle_id
                )

                if vehicle_type.lower() not in EMERGENCY_TYPES:
                    continue

                found_emergency_vehicle = True

                edge = traci.vehicle.getRoadID(
                    vehicle_id
                )

                speed = traci.vehicle.getSpeed(
                    vehicle_id
                )

                position = traci.vehicle.getLanePosition(
                    vehicle_id
                )

                print("\nREAL EMERGENCY VEHICLE FOUND")
                print("--------------------------------")
                print(f"Simulation time : {current_time}")
                print(f"Vehicle ID      : {vehicle_id}")
                print(f"Vehicle type    : {vehicle_type}")
                print(f"Current edge    : {edge}")
                print(f"Speed           : {speed}")
                print(f"Position        : {position}")

                break

            if found_emergency_vehicle:
                break

        assert found_emergency_vehicle, (
            "No emergency vehicle appeared within "
            "the first 300 simulation steps."
        )

        print(
            "\nReal SUMO emergency vehicle "
            "detection validation successful!"
        )

    finally:
        traci.close()


if __name__ == "__main__":
    test_real_sumo_emergency_vehicle()