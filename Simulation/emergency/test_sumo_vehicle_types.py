import traci


SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"

SUMO_CONFIG = (
    r"D:\Mini_Project\Quantum-Emergency-Routing"
    r"\sumo\emergency_simulation.sumocfg"
)


def test_sumo_vehicle_types():

    traci.start([
        SUMO_BINARY,
        "-c",
        SUMO_CONFIG
    ])

    try:
        for _ in range(5):

            traci.simulationStep()

            vehicle_ids = traci.vehicle.getIDList()

            print(
                f"\nSimulation time: "
                f"{traci.simulation.getTime()}"
            )

            for vehicle_id in vehicle_ids:

                vehicle_type = traci.vehicle.getTypeID(
                    vehicle_id
                )

                print(
                    f"{vehicle_id} -> "
                    f"type={vehicle_type}"
                )

        print(
            "\nSUMO vehicle type inspection successful!"
        )

    finally:
        traci.close()


if __name__ == "__main__":
    test_sumo_vehicle_types()