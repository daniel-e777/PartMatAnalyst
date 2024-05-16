from csv import DictReader

data = DictReader(open("2021-04-26_sds011_sensor_3659.csv"), delimiter = ";")

print(data.fieldnames)

for line in data: print(line)