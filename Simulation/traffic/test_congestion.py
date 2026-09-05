from Simulation.traffic.congestion import calculate_congestion_level


def main():

    print("Congestion Classification Test:")

    test_cases = [
        (13.89, 13.89),
        (10.0, 13.89),
        (7.0, 13.89),
        (3.0, 13.89),
        (0.0, 13.89),
        (10.0, 0.0),
    ]

    for current_speed, speed_limit in test_cases:

        result = calculate_congestion_level(
            current_speed=current_speed,
            speed_limit=speed_limit
        )

        print(
            f"Current speed={current_speed}, "
            f"Speed limit={speed_limit} "
            f"-> {result}"
        )


if __name__ == "__main__":
    main()