from logging import debug
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import *
from ttkbootstrap.colorutils import *
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
guiRoot.rowconfigure(0,weight=1)
guiRoot.columnconfigure(0,weight=1)
# Style setup
Style().theme_use('darkly')
# Style().configure("TFrame", padding=8, background="#000000", width=200)
# Style().configure("TLabel", background="#000", foreground="#00ff00")
# Style().configure("TCombobox", background="#777777", selectforeground="#00ff00", foreground="#ffffff")
# Style().configure("TButton", background="#444444")


# Top level frame
topFrame = Frame(guiRoot)
topFrame.grid(column=0,row=0, sticky=(N,S,E,W))

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

# Helps keep the layout centered
statsFrame = Frame(topFrame)

#Current stats labels
hueString = tk.StringVar()
labelHue = Label(statsFrame, width=10, textvariable=hueString)
hueString.set('Hue: ' + str(selectedLight.state.hue))

satString = tk.StringVar()
labelSat = Label(statsFrame, width=8, textvariable=satString)
satString.set('Sat: ' + str(selectedLight.state.saturation))

briString = tk.StringVar()
labelBri = Label(statsFrame, width=8, textvariable=briString)
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
    except : 
        debug('Could not set stat strings after fetching lights')
        return False
        

def toggleSelectedLight():
    selectedLight.toggle_on()
    return selectedLight.state.is_on
    
# Button to toggle selected light On/Off
toggleButton = Button(topFrame, width=25, text='Toggle Light', command=toggleSelectedLight)

# Component to select a new color using HSL
# It'll be a whole frame of it's own
colorFrame = Frame(topFrame, width=300)
cfLabel = Label(colorFrame, text='Change Color Options')

hueScaleNum = tk.IntVar()
hueWidth = 256
hueGradient = Canvas(colorFrame,width=hueWidth, height=25, borderwidth=1, relief='solid')
hueScale = Scale(colorFrame,orient=HORIZONTAL, length=hueWidth,from_=0, to=256, variable=hueScaleNum)

cfLabel.pack(side='top')
hueGradient.pack(side='top', padx=3)
hueScale.pack(side='top', padx=3)

# Hue_Api accepts [0, 2^16)
# We're gonna take in [0, 2^8)
# Might not be worth iterating through ALL of those 
# This can play around with color selection

# Gotta make a gradient to visibly select hue
# Need to make 255 steps out of 360 degrees for gradient
# Massaged the range to fit with an outline
for x in range(2,256):
    hueNum = int((x*360)/256)
    # The builtin colorutil function just does not like me
    # Doing the internal conversion by hand
    # print(ImageColor.getrgb(str('hsl('+str(hueNum)+',100%,50%)')))
    hr,hg,hb = ImageColor.getrgb(str('hsl('+str(hueNum)+',100%,50%)'))
    fillString = '#'+(f'{hr:02x}{hg:02x}{hb:02x}')
    hueGradient.create_rectangle(x,0,x+1,25, fill=fillString, outline=fillString)

#Separators
sepToggleToColorFrame = Separator(topFrame,orient='horizontal')

# Grid layout
lightSelectCombobox.grid(column=0,row=0,columnspan=6,rowspan=2, sticky=(W,E), padx=10)

labelHue.grid(column=0,row=0,columnspan=2, rowspan=1, sticky=(W))
labelSat.grid(column=2,row=0,columnspan=2, rowspan=1)
labelBri.grid(column=4,row=0,columnspan=2, rowspan=1, sticky=(E))
statsFrame.rowconfigure(0,weight=1)
statsFrame.columnconfigure(0,weight=1)
# statsFrame.columnconfigure(1,weight=1)
# statsFrame.columnconfigure(2,weight=1)
# statsFrame.columnconfigure(3,weight=1)
# statsFrame.columnconfigure(4,weight=1)
statsFrame.columnconfigure(5,weight=1)

statsFrame.grid(column=0, row=2, columnspan=6, sticky=(E,W), padx=10)
toggleButton.grid(column=0,columnspan=6, row=3, sticky=(N,S,E,W), padx=10)
sepToggleToColorFrame.grid(column=0,row=4,columnspan=6,padx=5, pady=10, sticky=(N,S,E,W))
colorFrame.grid(column=0, row=5, columnspan=6, sticky=(N,S,E,W))

#TODO replace with loop
topFrame.grid_rowconfigure(0,weight=1)
topFrame.grid_rowconfigure(1,weight=1)
topFrame.grid_rowconfigure(2,weight=1)
topFrame.grid_rowconfigure(3,weight=1)
topFrame.grid_rowconfigure(4,weight=1)
topFrame.grid_rowconfigure(5,weight=1)
topFrame.grid_columnconfigure(0,weight=1)
topFrame.grid_columnconfigure(1,weight=1)
topFrame.grid_columnconfigure(2,weight=1)
topFrame.grid_columnconfigure(3,weight=1)
topFrame.grid_columnconfigure(4,weight=1)
topFrame.grid_columnconfigure(5,weight=1)

guiRoot.mainloop()