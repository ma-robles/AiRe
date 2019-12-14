#!/usr/bin/python3

from tkinter import *

class reloadW:
    def __init__(self, master, var):
        self.master = master
        self.var = var
        self.reload()
    def reload(self,):
        filename = 'values.cca'
        with open(filename) as myfile:
            data = myfile.readline()[:-1]
        data = data.split(',')
        if len(data)>1:
            mdate,mtime = data[0].split()
            data.pop(0)
            data.insert(0,mtime)
            data.insert(0,mdate)
        for i,v in enumerate(self.var):
            try:
                v.set(data[i])
            except:
                v.set('---')
        self.master.after(1000, self.reload)

def my_entry(master, label, font=('Helvetica',18), **options):
    myframe = Frame(master)
    myframe.pack()
    Label(myframe, text=label, width=13, font=font, anchor=E).pack(side=LEFT)
    e = Entry(myframe, font=font, **options)
    e.pack()
    e.focus_set()
    return e

#font = ('Helvetica', 18)
width = 10
master = Tk()
master.title('Datos')
label_list = [
        'Date: ',
        'Time: ',
        'UV [index]: ',
        'Sun [W/m2]: ',
        'Wspeed [m/s]: ',
        'Wdir [°]: ',
        'Rain [mm]: ',
        'Temp [°C]: ',
        'RH [%]: ',
        'Pres [mbar]: ',
        'Bat [V]: ',
        ]
var = []
for l in label_list:
    var.append(StringVar())
    my_entry(master, l, textvariable=var[-1], width=width)
w = reloadW(master, var)
mainloop()
