from csv import DictReader

data = DictReader(open("2021-04-26_sds011_sensor_3659.csv"), delimiter = ";")

print(data.line_num)
print(data.fieldnames)

p1_sum = 0
p2_sum = 0

for line in data:
    print(line)
    print(data.line_num)
    p1_sum += float(line["P1"])
    p2_sum += float(line["P2"])

p1_avg = p1_sum / (data.line_num - 1)
p2_avg = p2_sum / (data.line_num - 1)
print(f"Average P1 value: {p1_avg}, average P2 value: {p2_avg}")