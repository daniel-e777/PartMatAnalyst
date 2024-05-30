from csv import DictReader

def evaluation(data):
    p1_values = []
    p2_values = []

    for line in data:
        print(line)
        print(data.line_num)
        p1_values.append(float(line["P1"]))
        p2_values.append(float(line["P2"]))

    p1_avg = sum(p1_values) / (data.line_num - 1)
    p1_max = max(p1_values)
    p2_avg = sum(p2_values) / (data.line_num - 1)
    p2_max = max(p2_values)
    print(f"Average P1 value: {p1_avg}, max. P1 value: {p1_max}.\nAverage P2 value: {p2_avg}, max. P2 value: {p2_max}.")

raw_data = DictReader(open("2021-04-26_sds011_sensor_3659.csv"), delimiter = ";")

print(raw_data.line_num)
print(raw_data.fieldnames)

evaluation(raw_data)