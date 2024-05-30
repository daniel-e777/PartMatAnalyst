import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from datetime import datetime

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer")
        self.root.geometry("1200x700")

        # Canvas erstellen
        self.canvas = tk.Canvas(root, width=1200, height=700)
        self.canvas.pack(fill="both", expand=True)

        # Hintergrundbild laden und skalieren
        self.bg_image = Image.open("orcaparadise.jpg")  # Update the path to your background image
        self.bg_image = self.bg_image.resize((1200, 700), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Menübutton und Datum/Uhrzeit
        self.menu_button = tk.Button(root, text="Menübutton")
        self.menu_button_window = self.canvas.create_window(10, 10, anchor="nw", window=self.menu_button)

        self.datetime_label_bg = tk.Label(root, bg="white", width=20)
        self.datetime_label_bg_window = self.canvas.create_window(1100, 10, anchor="ne", window=self.datetime_label_bg)

        self.datetime_label = tk.Label(root, text="", bg="white", width=20)
        self.datetime_label_window = self.canvas.create_window(1100, 10, anchor="ne", window=self.datetime_label)
        self.update_datetime()

        # Plot Bereich
        self.figure, self.ax = plt.subplots()
        self.canvas_figure = FigureCanvasTkAgg(self.figure, root)
        self.canvas_figure.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.canvas.create_window(20, 50, anchor="nw", window=self.canvas_figure.get_tk_widget())

        # Steuerbereich auf der rechten Seite
        self.controls_frame = tk.Frame(self.canvas)
        self.controls_frame_window = self.canvas.create_window(980, 50, anchor="nw", window=self.controls_frame)

        # Dateiauswahl
        self.file_button = tk.Button(self.controls_frame, text="Datei auswählen", command=self.load_csv)
        self.file_button.pack(pady=5)

        # Detailwerte
        self.details_label = tk.Label(self.controls_frame, text="Detailwerte (min, max, avg, Temp)")
        self.details_label.pack(pady=5)

        # Logo
        self.logo_image = Image.open("orcanado.png")  # Update the path to your logo
        self.logo_image = self.logo_image.resize((150, 150), Image.Resampling.LANCZOS)  # Resize the image
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self.controls_frame, image=self.logo_photo)
        self.logo_label.pack(pady=20)

        # Download Button
        self.download_button = tk.Button(self.controls_frame, text="Download")
        self.download_button.pack(pady=5)

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
                    if 'timestamp' in row and 'P1' in row and 'P2' in row:
                        row['timestamp'] = datetime.strptime(row['timestamp'], '%Y-%m-%dT%H:%M:%S')
                        data.append(row)
                    else:
                        messagebox.showerror("Fehler", "Die CSV-Datei muss die Spalten 'timestamp', 'P1' und 'P2' enthalten.")
                        return

            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['time_in_hours'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60 + df['timestamp'].dt.second / 3600
            df['P1'] = pd.to_numeric(df['P1'])
            df['P2'] = pd.to_numeric(df['P2'])
            
            if df.empty:
                messagebox.showinfo("Information", "Keine Daten gefunden.")
            else:
                self.plot_data(df)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {e}")

    def plot_data(self, df):
        self.ax.clear()
        self.ax.plot(df['time_in_hours'], df['P1'], marker='o', label='P1', alpha=0.7)
        self.ax.plot(df['time_in_hours'], df['P2'], marker='x', label='P2', alpha=0.7)
        self.ax.set_title('Messwerte von P1 und P2')
        self.ax.set_xlabel('Zeit (Stunden)')
        self.ax.set_ylabel('Werte (P1, P2)')
        self.ax.set_xticks(range(0, 25))  # Zeigt die Stunden von 0 bis 24
        self.ax.grid(True, alpha=0.7)
        self.ax.legend()
        self.canvas_figure.draw()

    def update_datetime(self):
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.config(text=current_time)
        self.root.after(1000, self.update_datetime)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()
