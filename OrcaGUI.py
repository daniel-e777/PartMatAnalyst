import tkinter as tk
from tkinter import filedialog, messagebox
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

bg_color = "#87cefa"

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer")
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
        self.menu_button = tk.Button(root, text="Menübutton", bg="#104e8b", fg="white")
        self.menu_button_window = self.canvas.create_window(40, 10, anchor="nw", window=self.menu_button)

        self.datetime_label_bg = tk.Label(root, bg=bg_color, width=20)
        self.datetime_label_bg_window = self.canvas.create_window(1147, 10, anchor="ne", window=self.datetime_label_bg)

        self.datetime_label = tk.Label(root, text="", bg=bg_color, width=20)
        self.datetime_label_window = self.canvas.create_window(1147, 10, anchor="ne", window=self.datetime_label)
        self.update_datetime()

        # Graph erstellen
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
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
            background="light blue",  # Hintergrundfarbe des Kalenders
            foreground="dark blue",   # Textfarbe des Kalenders
            selectbackground="dark blue",  # Hintergrundfarbe des ausgewählten Datums
            selectforeground="white"   # Textfarbe des ausgewählten Datums
        )
        self.start_date_calendar.pack(pady=5)

        # Kalender Widget für Enddatum
        self.end_date_label = tk.Label(self.controls_frame, text="Enddatum auswählen:", bg=bg_color)
        self.end_date_label.pack(pady=5)
        self.end_date_calendar = Calendar(
            self.controls_frame,
            selectmode='day',
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            background="light blue",  # Hintergrundfarbe des Kalenders
            foreground="dark blue",   # Textfarbe des Kalenders
            selectbackground="dark blue",  # Hintergrundfarbe des ausgewählten Datums
            selectforeground="white"   # Textfarbe des ausgewählten Datums
        )
        self.end_date_calendar.pack(pady=5)

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

        # Label for the background image
        self.loading_bg_label = tk.Label(self.root, image=self.bg_photo)
        self.loading_bg_label.place_forget()  

        # Loading GIF with the background image
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
        end_date = self.end_date_calendar.get_date()
        start_date_obj = datetime.strptime(start_date, "%m/%d/%y")
        end_date_obj = datetime.strptime(end_date, "%m/%d/%y")
        if end_date_obj < start_date_obj:
            messagebox.showerror("Fehler", "Enddatum darf nicht vor dem Startdatum liegen.")
            return

        date_list = [(start_date_obj + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date_obj - start_date_obj).days + 1)]

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
        try:
            data_frames = []
            for date_str in date_list:
                base_url = f"http://archive.sensor.community/{date_str}/"
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
                    continue

                soup = BeautifulSoup(response.content, "html.parser")
                file_name = None

                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href and 'sds011' in href and href.endswith('.csv'):
                        file_name = href
                        break

                if file_name:
                    file_url = f"{base_url}{file_name}"
                    local_file_path = os.path.join(os.getcwd(), file_name)
                    if not os.path.exists(local_file_path):
                        response = requests.get(file_url)
                        response.raise_for_status()
                        with open(local_file_path, 'wb') as file:
                            file.write(response.content)

                    df = self.load_csv(local_file_path, date_str)
                    if df is not None:
                        data_frames.append(df)
                else:
                    self.show_error(f"Keine Dateien für das Datum {date_str} gefunden.")

            if data_frames:
                self.df = pd.concat(data_frames, ignore_index=True)
                self.plot_data(date_list)
        except requests.RequestException as e:
            self.show_error(f"Fehler beim Herunterladen der Datei: {e}")
        finally:
            self.loading = False
            self.loading_bg_label.place_forget()
            self.loading_label.place_forget()

    def show_error(self, message):
        self.loading = False
        self.loading_bg_label.place_forget()
        self.loading_label.place_forget()
        messagebox.showerror("Fehler", message)

    def load_csv(self, file_path, date_str):
        data = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    if 'timestamp' in row and 'P1' in row and 'P2' in row:
                        row['timestamp'] = datetime.strptime(row['timestamp'], '%Y-%m-%dT%H:%M:%S')
                        data.append(row)
                    else:
                        self.show_error("Die CSV-Datei muss die Spalten 'timestamp', 'P1' und 'P2' enthalten.")
                        return None

            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            start_date = pd.to_datetime(date_str)
            df['day'] = (df['timestamp'].dt.normalize() - start_date.normalize()).dt.days
            df['time_in_hours'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60 + df['timestamp'].dt.second / 3600
            df['time_in_days'] = df['day'] + df['time_in_hours'] / 24
            df['P1'] = pd.to_numeric(df['P1'])
            df['P2'] = pd.to_numeric(df['P2'])

            return df
        except Exception as e:
            self.show_error(f"Fehler beim Laden der Datei: {e}")
            return None

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
        max_days = int(self.df['time_in_days'].max()) + 1
        x_ticks = []
        x_labels = []
        for day in range(max_days):
            for hour in range(24):
                x_ticks.append(day * 24 + hour)
                if hour == 0:
                    x_labels.append(f'Tag {day + 1}\n{hour:02d}:00')
                else:
                    x_labels.append(f'{hour:02d}:00')
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels(x_labels, rotation=45)
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