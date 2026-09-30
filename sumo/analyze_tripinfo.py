import xml.etree.ElementTree as ET
from collections import Counter

FILE = "congested_test.tripinfo.xml"
try:
    root = ET.parse(FILE).getroot()
except (FileNotFoundError, ET.ParseError) as e:
    print(f"Could not read {FILE}: {e}")
    raise SystemExit(1)

trips = root.findall("tripinfo")
if not trips:
    print("No completed trips found yet. Run SUMO first and then run this script.")
    raise SystemExit(0)

def f(a):
    try: return float(a)
    except: return 0.0

travel = sum(f(x.get('duration')) for x in trips)
waiting = sum(f(x.get('waitingTime')) for x in trips)
loss = sum(f(x.get('timeLoss')) for x in trips)
counts = Counter()
for x in trips:
    vid=x.get('id','')
    for t in ('car','motorcycle','taxi','bus','ambulance','police','firetruck'):
        if vid.startswith(t+'_'):
            counts[t]+=1
            break

print("===== SUMO TRAFFIC RESULTS =====")
print(f"Completed vehicles  : {len(trips)}")
print(f"Average travel time : {travel/len(trips):.2f} seconds")
print(f"Average waiting     : {waiting/len(trips):.2f} seconds")
print(f"Average time loss   : {loss/len(trips):.2f} seconds")
print("\nVehicle types in completed trips:")
for t in ('car','motorcycle','taxi','bus','ambulance','police','firetruck'):
    print(f"{t:12s}: {counts[t]}")
