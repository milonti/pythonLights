from logging import debug
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import *
from ttkbootstrap.constants import *
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
Style().theme_use('darkly')
# Style().configure("TFrame", padding=8, background="#000000", width=200)
# Style().configure("TLabel", background="#000", foreground="#00ff00")
# Style().configure("TCombobox", background="#777777", selectforeground="#00ff00", foreground="#ffffff")
# Style().configure("TButton", background="#444444")


# Top level frame
topFrame = Frame(guiRoot)
topFrame.grid(column=0,row=0)

def onLightComboChange(thing):
    selectLightByName(selectedName.get())
    
def selectLightByName(name):
    api.fetch_lights()
    global selectedLight
    for l in api.lights:
        if l.name == name:
            selectedLight = l
            set_stat_strings(selectedLight.state.hue, selectedLight.state.saturation, selectedLight.state.brightness)
            return True
    debug('Could not find light named: ' + str(name))
    return False

selectedName = tk.StringVar()
lightSelectCombobox = Combobox(topFrame, width=25,state='readonly', textvariable=selectedName)
vals = list(map(lambda x: x.name, reachables))
lightSelectCombobox['values'] = vals
lightSelectCombobox.current(0)
lightSelectCombobox.bind('<<ComboboxSelected>>', onLightComboChange)

#Current stats labels
hueString = tk.StringVar()
labelHue = Label(topFrame, width=10, textvariable=hueString)
hueString.set('Hue: ' + str(selectedLight.state.hue))

satString = tk.StringVar()
labelSat = Label(topFrame, width=8, textvariable=satString)
satString.set('Sat: ' + str(selectedLight.state.saturation))

briString = tk.StringVar()
labelBri = Label(topFrame, width=8, textvariable=briString)
briString.set('Bri: ' + str(selectedLight.state.brightness))

# Since changing *any* setting messes up the state object for a light
# Making two helper functions to set the stat strings more easily
def set_stat_strings(hue, sat, bright):
    hueString.set('Hue: ' + str(hue))
    satString.set('Sat: ' + str(sat))
    briString.set('Bri: ' + str(bright))
    
# Returns true if it made the attempt to set the info strings 
def fetch_light_stats():
    api.fetch_lights()
    name = selectedLight.name
    # Using one Hue Bridge which has some sort of a maximum on lights right?
    # And I believe they're limited to having unique names too
    for l in api.fetch_lights():
        if l.name == name:
            selectedLight = l
            break
        debug('Did not find light with name: ' + name)
        return False
    try:
        set_stat_strings(selectedLight.state.hue, selectedLight.state.saturation, selectedLight.state.brightness)
        return True
    except e: 
        debug('Could not set stat strings after fetching lights')
        return False
        

def toggleSelectedLight():
    selectedLight.toggle_on()
    return selectedLight.state.is_on
    
toggleButton = Button(topFrame, width=25, text='Toggle Light', command=toggleSelectedLight)

# Grid layout
lightSelectCombobox.grid(column=0,row=0,columnspan=6,rowspan=2)
labelHue.grid(column=0,row=2,columnspan=2, rowspan=1)
labelSat.grid(column=2,row=2,columnspan=2, rowspan=1)
labelBri.grid(column=4,row=2,columnspan=2, rowspan=1)
toggleButton.grid(column=1,columnspan=4, row=3)

guiRoot.mainloop()