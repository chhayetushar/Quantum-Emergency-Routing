import xml.etree.ElementTree as ET

# Load SUMO trip information
tree = ET.parse("congested_test.tripinfo.xml")
root = tree.getroot()

total_vehicles = 0
total_duration = 0
total_waiting = 0
total_time_loss = 0

for trip in root.findall("tripinfo"):
    total_vehicles += 1
    total_duration += float(trip.get("duration", 0))
    total_waiting += float(trip.get("waitingTime", 0))
    total_time_loss += float(trip.get("timeLoss", 0))

if total_vehicles > 0:
    average_duration = total_duration / total_vehicles
    average_waiting = total_waiting / total_vehicles
    average_time_loss = total_time_loss / total_vehicles

    print("===== SUMO CONGESTION RESULTS =====")
    print(f"Total vehicles     : {total_vehicles}")
    print(f"Average travel time: {average_duration:.2f} seconds")
    print(f"Average waiting    : {average_waiting:.2f} seconds")
    print(f"Average time loss  : {average_time_loss:.2f} seconds")
else:
    print("No trip information found.")