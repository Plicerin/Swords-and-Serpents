with open("traces/first_room_run/ss_trace_extended.txt") as f:
    lines = f.readlines()

# Extract around first 520A hit (line 1561 in zero-based is index 1560)
start = 1550
for i in range(start, min(start+30, len(lines))):
    line = lines[i].rstrip()
    if '520A' in line or '520B' in line or '520E' in line or '5212' in line or '526E' in line or 'MVI@ R4,R3' in line:
        print(f"{i+1:4d}: {line}")
