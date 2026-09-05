def calculate_congestion_level(
    current_speed: float,
    speed_limit: float
) -> str:

    if speed_limit <= 0:
        return "UNKNOWN"

    speed_ratio = current_speed / speed_limit

    if speed_ratio >= 0.80:
        return "LOW"

    elif speed_ratio >= 0.50:
        return "MEDIUM"

    elif speed_ratio >= 0.30:
        return "HIGH"

    else:
        return "SEVERE"