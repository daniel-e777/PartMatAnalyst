import tkinter as tk
from PIL import ImageTk
import sqlite3

#background color
bg_color = "#424a46"

#database connection ?
def fetch_db():
    connection = sqlite3.connect("part_mat_data.db")
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS
    sensordata(timestamp str, sensorid int, pm25 float, pm10 float, location str)""")

def do_something ():
    print("I did something")

def load_startscreen():
    startscreen.pack_propagate(False)
    tk.Label(startscreen,text="Willkommen bei Partmatanalyst",bg=bg_color,fg="white",font=("TkMenuFont",14)).pack()

    logo_img=ImageTk.PhotoImage(file="orcanado.png")
    logo_widget=tk.Label(startscreen, image=logo_img, bg= bg_color)
    logo_widget.image = logo_img
    logo_widget.pack()

    #button
    tk.Button(startscreen,text="Start",font=("TkHeadingFont",20),bg="black",fg="white",cursor="hand2",command=lambda:load_mainscreen()).pack(pady=20)

def load_mainscreen():
        
    mainscreen.pack_propagate(False)
    tk.Label(mainscreen,text="Willkommen bei Partmatanalyst",bg=bg_color,fg="white",font=("TkMenuFont",14)).pack()

    logo_img=ImageTk.PhotoImage(file="orcanado.png")
    logo_widget=tk.Label(mainscreen, image=logo_img, bg= bg_color)
    logo_widget.image = logo_img
    logo_widget.pack()

    #button
    tk.Button(mainscreen,text="Start",font=("TkHeadingFont",20),bg="black",fg="white",cursor="hand2",command=lambda:do_something()).pack(pady=20)


#app starten
window = tk.Tk()
window.title("Partmatanalyst")
window.eval("tk::PlaceWindow . center")



#app dimensionen und zentrierung
startscreen = tk.Frame(window, width=900, height= 600, bg=bg_color)
mainscreen = tk.Frame(window, width=1200, height= 1000, bg=bg_color)
startscreen.grid(row=0,column=0)
mainscreen.grid(row=1,column=1)

#for screen in (startscreen,mainscreen):
 #   screen.grid(row=0,column = 0)



load_startscreen()

#run app
window.mainloop()