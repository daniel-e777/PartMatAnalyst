import matplotlib.pyplot as plt
import numpy as np

import matplotlib as mpl
from csv import DictReader
from datetime import datetime

def plot_temperature_changes(file_path):
    # Reading the CSV file
    data = DictReader(open(file_path, 'r'), delimiter=';')
    
    timestamps = []
    temperatures = []
    
    for line in data:
        timestamp = datetime.strptime(line['timestamp'], '%Y-%m-%d %H:%M:%S') # Adjust the format as per your CSV
        temperature = float(line['temperature'])
        
        timestamps.append(timestamp)
        temperatures.append(temperature)
        
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, temperatures, label='Temperature', color='tab:blue')
    
    # Formatting the plot
    plt.title('Temperature Changes Throughout the Day')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Use DateFormatter to format the x-axis labels
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1)) # Adjust as necessary for your data's timestamp frequency
    
    plt.legend()
    plt.grid(True)
    
    plt.show()

# Replace 'your_file_path.csv' with the path to your CSV file
plot_temperature_changes('2021-04-26_dht22_sensor_3660.csv')