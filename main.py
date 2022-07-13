import tkinter as tk
from tkinter.ttk import *
from hue_api import HueApi

# HueApi user assumed to be previously created and saved 
api = HueApi()
api.load_existing()

# Fetch all the info from the bridge
api.fetch_lights()
api.fetch_groups()
api.fetch_scenes()

# List of reachable (online) lights
reachables = []
for light in api.lights:
    if light.state.reachable:
        reachables.append(light)
        print(light.name + ' is reachable')
    
print('Total reached: ' + str(len(reachables)))
print('Selecting default: ' + str(reachables[0].name))
selectedLight = reachables[0]

guiRoot = tk.Tk()

# Style setup
Style().configure("TFrame", padding=8, background="#000000")
Style().configure("TLabel", background="#000", foreground="#00ff00")
Style().configure("Combobox", background="#555555",foreground="#ffffff")


# Top level frame
topFrame = Frame(guiRoot)
topFrame.grid(column=0,row=0)


lightSelectSpinbox = Combobox(topFrame, width=25,state='readonly')
vals = list(map(lambda x: x.name, reachables))
lightSelectSpinbox['values'] = vals

hueString = tk.StringVar()
labelHue = Label(topFrame, width=10, foreground="#00ff00", textvariable=hueString)
hueString.set('Hue: ' + str(selectedLight.state.hue))

satString = tk.StringVar()
labelSat = Label(topFrame, width=8, foreground="#00ff00", textvariable=satString)
satString.set('Sat: ' + str(selectedLight.state.saturation))

briString = tk.StringVar()
labelBri = Label(topFrame, width=8, foreground="#00ff00", textvariable=briString)
briString.set('Bri: ' + str(selectedLight.state.brightness))

def toggleSelectedLight():
    selectedLight.toggle_on()
    return selectedLight.state.is_on
    
toggleButton = Button(topFrame, width=100,text='Toggle Light', command=toggleSelectedLight)

# Grid layout
lightSelectSpinbox.grid(column=0,row=0,columnspan=6,rowspan=2)
labelHue.grid(column=0,row=2,columnspan=2, rowspan=1)
labelSat.grid(column=2,row=2,columnspan=2, rowspan=1)
labelBri.grid(column=4,row=2,columnspan=2, rowspan=1)
toggleButton.grid(column=1,columnspan=4, row=3)

guiRoot.mainloop()