import tkinter as tk
from tkinter import filedialog, messagebox
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

        # Menübutton und Datum/Uhrzeit
        self.menu_button = tk.Button(root, text="Menübutton")
        self.menu_button.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)

        self.datetime_label = tk.Label(root, text="Datum Uhrzeit")
        self.datetime_label.pack(side=tk.TOP, anchor=tk.E, padx=10, pady=10)

        # Plot Bereich
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, root)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Steuerbereich auf der rechten Seite
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

        # Dateiauswahl
        self.file_button = tk.Button(self.controls_frame, text="Datei auswählen", command=self.load_csv)
        self.file_button.pack(pady=5)

        # Detailwerte
        self.details_label = tk.Label(self.controls_frame, text="Detailwerte (min, max, avg, Temp)")
        self.details_label.pack(pady=5)

        # Logo
        self.logo_label = tk.Label(self.controls_frame, text="LOGO PLATZHALTER", fg="blue")
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
        self.ax.plot(df['time_in_hours'], df['P1'], marker='o', label='P1')
        self.ax.plot(df['time_in_hours'], df['P2'], marker='x', label='P2')
        self.ax.set_title('Messwerte von P1 und P2')
        self.ax.set_xlabel('Zeit (Stunden)')
        self.ax.set_ylabel('Werte (P1, P2)')
        self.ax.set_xticks(range(0, 25))  # Zeigt die Stunden von 0 bis 24
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()
