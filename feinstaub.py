import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from datetime import datetime
from tkcalendar import Calendar  
import sqlite3
import requests

bg_color = "#87cefa"

 









class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Partmatanalyst")
        self.root.geometry("1200x700")

        # Canvas erstellen
        self.canvas = tk.Canvas(root, width=1200, height=700)
        self.canvas.pack(fill="both", expand=True)

        # Hintergrundbild laden und skalieren
        self.bg_image = Image.open("orcaparadise.jpg")
        self.bg_image = self.bg_image.resize((1200, 700), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Menübutton und Datum/Uhrzeit
        self.menu_button = tk.Button(root, text="Appschließen (lol)", bg="#104e8b", fg="white", command=quit)
        self.menu_button_window = self.canvas.create_window(40, 10, anchor="nw", window=self.menu_button)

       

        # Uhrzeit und Datum

        self.datetime_label_bg = tk.Label(root, bg=bg_color, width=20)
        self.datetime_label_bg_window = self.canvas.create_window(1175, 10, anchor="ne", window=self.datetime_label_bg)

        self.datetime_label = tk.Label(root, text="", bg=bg_color, width=20)
        self.datetime_label_window = self.canvas.create_window(1175, 10, anchor="ne", window=self.datetime_label, width = 280)
        self.update_datetime()

        # Graph erstellen
        self.figure, self.ax = plt.subplots(figsize=(8, 5))  
        self.figure.patch.set_facecolor("#87cefa")
        self.ax.imshow(self.bg_image, aspect='auto', extent=[0, 10, 0, 10], zorder=-1)
        self.canvas_figure = FigureCanvasTkAgg(self.figure, root)
        self.canvas_figure.get_tk_widget().pack(side=tk.LEFT, padx=20, pady=20)
        self.canvas.create_window(40, 100, anchor="nw", window=self.canvas_figure.get_tk_widget())
        
        # Steuerbereich auf der rechten Seite
        self.controls_frame = tk.Frame(self.canvas, bg=bg_color)
        self.controls_frame_window = self.canvas.create_window(897, 100, anchor="nw", window=self.controls_frame, width= 280, height= 500)

        

        # Dateiauswahl
        self.file_button = tk.Button(self.controls_frame, text="Datei auswählen", command=self.load_csv, bg="#104e8b", fg="white")
        self.file_button.pack(pady=5)

        # Logo
        self.logo_image = Image.open("orca.png")
        self.logo_image = self.logo_image.resize((150, 150), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self.controls_frame, image=self.logo_photo)
        self.logo_label.pack(pady=20)

        # Sensor-ID-Label und Eingabe
        self.sensor_id_label = tk.Label(self.controls_frame, text="Sensor ID:")
        self.sensor_id_label.pack()
        self.sensor_id_input = tk.Entry(self.controls_frame, bg="#104e8b", fg="white")
        #self.input_window = self.canvas.create_window(945, 275,anchor="nw", window=self.input)
       
        self.sensor_id_input.pack(pady=5)

      

        # Kalender Widget
        self.calendar = Calendar(
            self.controls_frame, 
            selectmode='day', 
            year=datetime.now().year, 
            month=datetime.now().month, 
            day=datetime.now().day,
            background="light blue",
            foreground="dark blue",  
            selectbackground="dark blue",  
            selectforeground="white",
            date_pattern="yyyy-mm-dd"
            )
        self.calendar.pack()
        #self.calendar_window = self.canvas.create_window(900, 400, anchor="nw", window=self.calendar)

        self.select_button = tk.Button(self.controls_frame,text="Auswählen", command=self.url_data , bg="#104e8b", fg="white")
        self.select_button.pack(side= "left")
        

          # Download Button
        self.download_button = tk.Button(self.controls_frame, text="Speichern", command=self.check_and_update_database , bg="#104e8b", fg="white")
        self.download_button.pack(side = "right")

    def generate_url(j,datum, sensor_id, url):
        date_url = datum
        url = "https://archive.sensor.community"
        sensor_url = f"_sds011_sensor_{sensor_id}"
        gesamt_url = f"{url}/{date_url}/{date_url}{sensor_url}.csv"
        print(gesamt_url)
        return gesamt_url
        
    

    def url_data(self):
        datum= self.calendar.get_date()
        sensor_id = self.sensor_id_input.get()
        url = "https://archive.sensor.community/"

        self.generate_url(datum, sensor_id,url) 
        

    def check_and_update_database(self,datum,gesamt_url):
        conn = sqlite3.connect('part_mat_data.db')
        cursor = conn.cursor()
        datum_start = str(datum)
        datum_end = str(datum)
        
        
        # Erstelle die Tabelle, falls sie nicht existiert
        cursor.execute("""CREATE TABLE IF NOT EXISTS sensordata (
                        timestamp TEXT,
                        sensorid INTEGER,
                        p1 REAL,
                        p2 REAL,
                        location TEXT)""")
        cursor.execute("SELECT COUNT(*) FROM sensordata WHERE timestamp BETWEEN ? AND ?", (datum_start,datum_end))
        count = cursor.fetchone()[0]
        download_data = requests.get(gesamt_url)
        if count == 0:
            
            # Bestimme die Jahre und Monate im Zeitraum
            datum_start = datetime.strptime(datum, '%Y-%m-%d')
            datum_end = datetime.strptime(datum, '%Y-%m-%d')
            
            # Schleife durch die Monate im Zeitraum
            current_dt = datum_start
            while current_dt <= datum_end:
                df = generate_url(datum.year, datum.month)
                if df is not None:
                    # Filtere die Daten für den spezifischen Zeitraum
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df[(df['timestamp'] >= datum_start) & (df['timestamp'] <= datum_end)]
                    df.to_sql('sensordata', conn, if_exists='append', index=False)
                current_dt = (current_dt.replace(day=1) + pd.DateOffset(months=1))
            
            messagebox.showinfo("Erfolg", "Daten erfolgreich heruntergeladen und in die Datenbank eingefügt")
        else:
            messagebox.showinfo("Information", "Daten für diesen Zeitraum sind bereits in der Datenbank")
        
        conn.commit()
        conn.close()


    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Wählen Sie die CSV-Datei",
            filetypes=[("CSV files", "*.csv")],
            initialdir="."
        )
        
        if not file_path:
            messagebox.showwarning("Warnung", "Keine Datei ausgewählt!")
            return
        
        try:
            data = []
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    if 'timestamp' in row and 'temperature' in row:
                        row['timestamp'] = datetime.strptime(row['timestamp'], '%Y-%m-%dT%H:%M:%S')
                        data.append(row)
                    else:
                        messagebox.showerror("Fehler", "Die CSV-Datei muss die Spalten 'timestamp' und 'temperature' enthalten.")
                        return

            self.df = pd.DataFrame(data)
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df['time_in_hours'] = self.df['timestamp'].dt.hour + self.df['timestamp'].dt.minute / 60 + self.df['timestamp'].dt.second / 3600
            self.df['temperature'] = pd.to_numeric(self.df['temperature'])
            
            if self.df.empty:
                messagebox.showinfo("Information", "Keine Daten gefunden.")
            else:
                self.plot_data()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {e}")

    def plot_data(self):
        self.ax.clear()

        # Datum aus den Daten extrahieren
        date_str = self.df['timestamp'].dt.date.iloc[0].strftime('%d.%m.%Y')

        # Plot für Temperatur
        self.ax.plot(self.df['time_in_hours'], self.df['temperature'], color='black', alpha=0.7)
        self.ax.set_title(f'Temperatur am {date_str}')
        self.ax.set_xlabel('Zeit in Stunden')
        self.ax.set_ylabel('Temperatur (°C)')
        self.ax.set_xlim(0, 24)
        self.ax.set_xticks(range(0, 25))
        self.ax.set_xticklabels(range(0, 25)) 
        self.ax.grid(True, alpha=0.5)
        self.ax.legend(['Temperature'])

        self.canvas_figure.draw()

    def download_plot(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Speichern unter"
        )
        if file_path:
            try:
                self.figure.savefig(file_path)
                messagebox.showinfo("Erfolg", "Der Graph wurde erfolgreich gespeichert.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern des Graphen: {e}")

    def update_datetime(self):
        now = datetime.now()
        current_time = now.strftime("%d.%m.%Y %H:%M:%S")
        self.datetime_label.config(text=current_time)
        self.root.after(1000, self.update_datetime)



            
    # App schließen
    def quit():
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()
