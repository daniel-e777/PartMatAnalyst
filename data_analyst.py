from csv import DictReader

data = DictReader(open("2021-04-26_sds011_sensor_3659.csv"), delimiter = ";")

print(data.fieldnames)
sum = 0
for line in data:
    print(line)
    sum += float(line["P1"])

avg = sum / (data.line_num - 1)
print(avg)