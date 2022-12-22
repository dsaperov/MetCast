import sys

incoming_input = []

for line in sys.stdin:
    incoming_input.append(line.rstrip())

for day_forecast in incoming_input[-19:-2]:
    print(day_forecast)
