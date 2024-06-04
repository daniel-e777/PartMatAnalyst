from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Dummy_data import sales_data, inventory_data, product_data, sales_year_data, inventory_month_data


#colors 
plt.rcParams["axes.prop_cycle"] = plt.cycler(
    color=["#4C2A85", "#BE96FF", "#957DAD", "#5E366E", "#A98CCC"])

# Line chart of sales by year
fig4, ax4 = plt.subplots()
ax4.plot(list(sales_year_data.keys()), list(sales_year_data.values()))
ax4.set_title("Sales by Year")
ax4.set_xlabel("Year")
ax4.set_ylabel("Sales")
# plt.show()



#Erstellen eines Windows
window = Tk()
window.title("PratMatAnalyst")
window.state('zoomed')

#set window size
#window.geometry("900x150")



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