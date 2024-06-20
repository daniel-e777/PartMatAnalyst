import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageSequence
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from datetime import datetime, timedelta
from tkcalendar import Calendar
import os
import requests
from bs4 import BeautifulSoup
import threading
import time
import sqlite3
import io
import gzip

bg_color = "#87cefa"

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PartMatAnalyst")
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
        # self.menu_button = tk.Button(root, text="Menübutton", bg="#104e8b", fg="white")
        # self.menu_button_window = self.canvas.create_window(40, 10, anchor="nw", window=self.menu_button)

        self.datetime_label_bg = tk.Label(root, bg=bg_color, width=20)
        self.datetime_label_bg_window = self.canvas.create_window(1147, 10, anchor="ne", window=self.datetime_label_bg)

        self.datetime_label = tk.Label(root, text="", bg=bg_color, width=20)
        self.datetime_label_window = self.canvas.create_window(1147, 10, anchor="ne", window=self.datetime_label)
        self.update_datetime()

        # Graph erstellen
        self.figure, self.ax = plt.subplots(figsize=(8.5, 5.5))
        self.figure.patch.set_facecolor("#87cefa")
        self.ax.imshow(self.bg_image, aspect='auto', extent=[0, 10, 0, 10], zorder=-1)
        self.canvas_figure = FigureCanvasTkAgg(self.figure, root)
        self.canvas_figure.get_tk_widget().pack(side=tk.LEFT, padx=20, pady=20)
        self.canvas.create_window(40, 100, anchor="nw", window=self.canvas_figure.get_tk_widget())

        # Steuerbereich auf der rechten Seite
        self.controls_frame = tk.Frame(self.root, bg=bg_color)
        self.controls_frame.place(x=900, y=100, anchor="nw")

        # Kalender Widget für Startdatum
        self.calendar_label = tk.Label(self.controls_frame, text="Startdatum auswählen:", bg=bg_color)
        self.calendar_label.pack(pady=5)
        self.start_date_calendar = Calendar(
            self.controls_frame,
            selectmode='day',
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            background="light blue",
            foreground="dark blue",
            selectbackground="dark blue",
            selectforeground="white"
        )
        self.start_date_calendar.pack(pady=5)

        # Dropdown für Anzahl der Tage
        self.days_label = tk.Label(self.controls_frame, text="Anzahl der Tage auswählen:", bg=bg_color)
        self.days_label.pack(pady=5)
        self.days_var = tk.IntVar(value=1)
        self.days_dropdown = ttk.Combobox(self.controls_frame, textvariable=self.days_var, values=[i for i in range(1, 31)])
        self.days_dropdown.pack(pady=5)

        # Bestätigungsbutton
        self.confirm_button = tk.Button(self.controls_frame, text="Daten laden", command=self.on_confirm, bg="#104e8b", fg="white")
        self.confirm_button.pack(pady=5)

        # Logo
        self.logo_image = Image.open("orca.png")
        self.logo_image = self.logo_image.resize((150, 150), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self.controls_frame, image=self.logo_photo)
        self.logo_label.pack(pady=20)

        # Download Button
        self.download_button = tk.Button(self.controls_frame, text="Speichern", command=self.download_plot, bg="#104e8b", fg="white")
        self.download_button.pack(pady=5)

        # Label für Hintergrundbild
        self.loading_bg_label = tk.Label(self.root, image=self.bg_photo)
        self.loading_bg_label.place_forget()

        # Loading GIF mit Hintergrundbild
        self.loading_gif = Image.open("orcas.gif")
        self.loading_frames = [self.overlay_gif_on_bg(frame) for frame in ImageSequence.Iterator(self.loading_gif)]
        self.loading_label = tk.Label(self.root)
        self.loading_label.place_forget()

        self.loading = False

    def overlay_gif_on_bg(self, gif_frame):
        """Overlay the GIF frame on the background image."""
        bg_image = self.bg_image.copy()
        gif_frame = gif_frame.convert("RGBA").resize((500, 500), Image.Resampling.LANCZOS)
        bg_image.paste(gif_frame, (350, 100), gif_frame)
        return ImageTk.PhotoImage(bg_image)

    def on_confirm(self):
        start_date = self.start_date_calendar.get_date()
        start_date_obj = datetime.strptime(start_date, "%m/%d/%y")
        num_days = self.days_var.get()

        date_list = [(start_date_obj + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_days)]

        self.loading = True
        self.loading_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        threading.Thread(target=self.animate_loading).start()

        thread = threading.Thread(target=self.download_and_load_csv, args=(date_list,))
        thread.start()

    def animate_loading(self):
        def next_frame(frame_index=0):
            if self.loading:
                frame = self.loading_frames[frame_index]
                self.loading_label.config(image=frame)
                frame_index = (frame_index + 1) % len(self.loading_frames)
                self.root.after(50, next_frame, frame_index)

        next_frame()

    def download_and_load_csv(self, date_list):
        conn = sqlite3.connect("part_mat_data.db")
        self.create_table(conn)
        try:
            data_frames = []
            for date_str in date_list:
                df = self.check_database(conn, date_str)
                if df is None:
                    df = self.download_csv(date_str)
                    if df is not None:
                        self.save_to_database(conn, date_str, df)
                if df is not None:
                    df = self.process_dataframe(df, date_str)
                    data_frames.append(df)

            if data_frames:
                self.df = pd.concat(data_frames, ignore_index=True)
                self.plot_data(date_list)
        except Exception as e:
            self.show_error(f"Fehler beim Verarbeiten der Daten: {e}")
        finally:
            conn.close()
            self.loading = False
            self.loading_bg_label.place_forget()
            self.loading_label.place_forget()

    def create_table(self, conn):
        """Create the table if it doesn't exist."""
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    data BLOB
                )
            """)

    def check_database(self, conn, date_str):
        """Check if the data for the given date is in the database."""
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM sensor_data WHERE date = ?", (date_str,))
        row = cursor.fetchone()
        if row:
            data = row[0]
            return pd.read_csv(io.StringIO(data.decode('utf-8')), delimiter=';')
        return None

    def save_to_database(self, conn, date_str, df):
        """Save the data to the database."""
        data = df.to_csv(index=False, sep=';').encode('utf-8')
        with conn:
            conn.execute("INSERT INTO sensor_data (date, data) VALUES (?, ?)", (date_str, data))

    def download_csv(self, date_str):
        """Download the CSV file for the given date."""
        try:
            year = date_str.split('-')[0]
            if int(year) <= 2022:
                base_url = f"http://archive.sensor.community/{year}/{date_str}/"
            else:
                base_url = f"http://archive.sensor.community/{date_str}/"

            print(f"Attempting to access URL: {base_url}")  # Debugging information

            retries = 3
            for _ in range(retries):
                try:
                    response = requests.get(base_url, timeout=10)
                    response.raise_for_status()
                    break
                except requests.RequestException:
                    time.sleep(5)
            else:
                self.show_error(f"Fehler beim Herunterladen der Datei: {base_url}")
                return None

            soup = BeautifulSoup(response.content, "html.parser")
            file_name = None

            for link in soup.find_all('a'):
                href = link.get('href')
                if href and 'sds011' in href and (href.endswith('.csv') or href.endswith('.csv.gz')):
                    file_name = href
                    break

            if file_name:
                file_url = f"{base_url}{file_name}"
                print(f"Downloading file from URL: {file_url}")  # Debugging information
                response = requests.get(file_url)
                response.raise_for_status()
                if file_name.endswith('.gz'):
                    with gzip.open(io.BytesIO(response.content), 'rt') as f:
                        df = pd.read_csv(f, delimiter=';')
                else:
                    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), delimiter=';')
                return df
            else:
                self.show_error(f"Keine Dateien für das Datum {date_str} gefunden.")
                return None
        except Exception as e:
            self.show_error(f"Fehler beim Herunterladen der Datei: {e}")
            return None

    def process_dataframe(self, df, date_str):
        """Process the dataframe to add necessary columns."""
        start_date = pd.to_datetime(date_str)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['day'] = (df['timestamp'].dt.normalize() - start_date.normalize()).dt.days
        df['time_in_hours'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60 + df['timestamp'].dt.second / 3600
        df['time_in_days'] = df['day'] + df['time_in_hours'] / 24
        df['P1'] = pd.to_numeric(df['P1'])
        df['P2'] = pd.to_numeric(df['P2'])
        return df

    def show_error(self, message):
        self.loading = False
        self.loading_bg_label.place_forget()
        self.loading_label.place_forget()
        messagebox.showerror("Fehler", message)

    def plot_data(self, date_list):
        self.ax.clear()

        # Plot für P1 und P2
        self.ax.plot(self.df['time_in_days'] * 24, self.df['P1'], color='blue', alpha=0.7, label='P1')
        self.ax.plot(self.df['time_in_days'] * 24, self.df['P2'], color='green', alpha=0.7, label='P2')

        start_date = date_list[0]
        end_date = date_list[-1]
        self.ax.set_title(f'P1 und P2 vom {start_date} bis {end_date}')

        self.ax.set_xlabel('Zeit in Stunden')
        self.ax.set_ylabel('Konzentration (µg/m³)')
        max_days = int(self.df['day'].max()) + 1

        x_ticks = []
        x_labels = []

        if len(date_list) == 1:
            # für einzelne Tage
            for hour in range(25):  
                x_ticks.append(hour)
                x_labels.append(str(hour))
        else:
            # für mehrere Tage (X-Achse: Tag 1, Tag 2...)
            for day in range(max_days):
                for hour in range(24):
                    x_ticks.append(day * 24 + hour)
                    if hour == 0:
                        x_labels.append(f'Tag {day + 1}\n{hour}')
                    else:
                        x_labels.append(str(hour))
                x_ticks.append((day + 1) * 24)
                x_labels.append(f'Tag {day + 1}\n24')

        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels(x_labels, rotation=45)
        self.ax.set_xlim(left=0, right=x_ticks[-1])
        self.ax.grid(True, alpha=0.5)
        self.ax.legend()

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
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern des Graphen: {e}")

    def update_datetime(self):
        now = datetime.now()
        current_time = now.strftime("%d.%m.%Y %H:%M:%S")
        self.datetime_label.config(text=current_time)
        self.root.after(1000, self.update_datetime)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()
