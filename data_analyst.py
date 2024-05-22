from csv import DictReader

data = DictReader(open("2021-04-26_sds011_sensor_3659.csv"), delimiter = ";")

print(data.line_num)
print(data.fieldnames)

sum = 0
for line in data:
    print(line)
    print(data.line_num)
    sum += float(line["P1"])

avg = sum / (data.line_num -1)
print(f"Average P1 value: {avg}")