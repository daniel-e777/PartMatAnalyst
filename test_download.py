import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3
import requests
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime

def generate_url(j, start_datum, end_datum, sensor_typ, sensor_id, url):
    current_date = date.today()
    start_monat, start_jahr = map(int, start_datum.split("/"))
    end_monat, end_jahr = map(int, end_datum.split("/"))
    start_monat if j == start_jahr else 1  # hilfsvariable falls endmonat kleiner als startmonat
    end_monat if j == end_jahr else 12

    date_url = f"{j:04d}-{m:02d}-{t:02d}"
    sensor_url = f"_{sensor_typ}_sensor_{sensor_id}"
    gesamt_url = f"{url}{j}/{date_url}/{date_url}{sensor_url}.csv"
    print(gesamt_url)

def url_data():
    start_datum = start_date_calendar.get_date()
    end_datum = end_date_calendar.get_date()
    sensor_typ = sensor_type_combobox.get()
    sensor_id = sensor_id_entry.get()

    generate_url(start_datum, end_datum, sensor_typ, sensor_id)  

# Funktion zum Herunterladen der Feinstaubwerte von sensor.community (nur SDS011-Sensoren)
def download_sensor_data(year, month):
    base_url = "http://archive.sensor.community/"
    formatted_month = f"{month:02d}"
    file_name = f"{year}-{formatted_month}/"
    url = base_url + file_name

    # Herunterladen der ZIP-Datei
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Erfolgreich heruntergeladen: {file_name}")
        zipfile = ZipFile(BytesIO(response.content))
        
        # Extrahiere und lese die CSV-Dateien, die "sds011" im Namen enthalten
        csv_files = [f for f in zipfile.namelist() if 'sds011' in f and f.endswith('.csv')]
        data_frames = []
        
        for csv_file in csv_files:
            with zipfile.open(csv_file) as file:
                df = pd.read_csv(file)
                data_frames.append(df)
        
        # Zusammenführen aller DataFrames
        if data_frames:
            combined_df = pd.concat(data_frames, ignore_index=True)
            return combined_df
        else:
            print("Keine relevanten CSV-Dateien im ZIP-Archiv gefunden.")
            return None
    else:
        print(f"Fehler beim Herunterladen der Datei: {file_name}")
        return None

# Funktion zum Überprüfen der Datenbank und Einfügen neuer Daten
def check_and_update_database(start_date, end_date):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # Erstelle die Tabelle, falls sie nicht existiert
    cursor.execute("""CREATE TABLE IF NOT EXISTS
    sensordata(timestamp str, sensorid int, pm25 float, pm10 float, location str)""")
    
    # Überprüfe, ob Daten im Zeitraum bereits vorhanden sind
    cursor.execute("SELECT COUNT(*) FROM data WHERE timestamp BETWEEN ? AND ?", (start_date, end_date))
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Bestimme die Jahre und Monate im Zeitraum
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Schleife durch die Monate im Zeitraum
        current_dt = start_dt
        while current_dt <= end_dt:
            df = download_sensor_data(current_dt.year, current_dt.month)
            if df is not None:
                # Filtere die Daten für den spezifischen Zeitraum
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df[(df['timestamp'] >= start_dt) & (df['timestamp'] <= end_dt)]
                df.to_sql('data', conn, if_exists='append', index=False)
            current_dt = (current_dt.replace(day=1) + pd.DateOffset(months=1))
        
        messagebox.showinfo("Erfolg", "Daten erfolgreich heruntergeladen und in die Datenbank eingefügt")
    else:
        messagebox.showinfo("Information", "Daten für diesen Zeitraum sind bereits in der Datenbank")
    
    conn.commit()
    conn.close()

# Hauptanwendungsfenster
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Datenüberprüfung und -aktualisierung")
        
        tk.Label(self, text="Startdatum:").grid(row=0, column=0, padx=10, pady=10)
        self.start_date_entry = DateEntry(self, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self, text="Enddatum:").grid(row=1, column=0, padx=10, pady=10)
        self.end_date_entry = DateEntry(self, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Button(self, text="Überprüfen und aktualisieren", command=self.check_and_update).grid(row=2, column=0, columnspan=2, pady=10)

    def check_and_update(self):
        start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
        end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')
        check_and_update_database(start_date, end_date)

# Starte die Anwendung
if __name__ == "__main__":
    app = Application()
    app.mainloop()
