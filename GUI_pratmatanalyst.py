from tkinter import *

#Erstellen eines Windows
window = Tk()
window.title("PratMatAnalyst")

#set window size
window.geometry("900x150")

#scale up window
window.tk.call("tk","scaling", 3.0)

#Define function of buttons
def btn2_clicked():
    window.destroy()


#create label

lbl = Label(window, text= "Nach Datum suchen")
lbl.grid(column=8, row = 0)

#create buttons

btn1 = Button(window, text="test1")
btn1.grid(column=8,row=2)

btn2 = Button(window, text="test2", command = btn2_clicked)
btn2.grid(column=9,row=2)




window.mainloop()