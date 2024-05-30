from csv import DictReader

def analyze_csv_temperature(file_path):
    data = DictReader(open("2021-04-26_dht22_sensor_3660.csv"), delimiter = ";")

    max_temp = float("-inf")
    max_temp_line = None
    min_temp = float("inf")
    min_temp_line = None
    sum_temp = float(0)
    count_temp = 0

    for line in data:
        Zeilennummer = data.line_num
        timestamp = line['timestamp']
        temperatur = float(line['temperature'])
        sum_temp += temperatur
        count_temp += 1

        if temperatur > max_temp:
                max_temp = temperatur
                max_temp_line = Zeilennummer
        
        if temperatur < min_temp:
              min_temp = temperatur
              min_temp_line = Zeilennummer

    if count_temp > 0:
        avg_temp = sum_temp / count_temp
        result = (f"Durchschnittstemperatur: {round(avg_temp, 2)}°C\n"
                  f"Höchste Temperatur: {max_temp}°C, gefunden in Zeile: {max_temp_line}\n"
                  f"Niedrigste Temperatur: {min_temp}°C, gefunden in Zeile: {min_temp_line}\n"
                  f"Temperaturdifferenz: {round(max_temp - min_temp, 2)}°C")
    else:
        result = "Keine Temperaturdaten gefunden."
    
    return result
