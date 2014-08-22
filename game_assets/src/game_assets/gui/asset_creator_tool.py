import Tkinter as tk
import tkFont
import ttk

class AssetCreatorTool(object):
    
    class Constants(object):
        
        WINDOW_WIDTH = 800
        WINDOW_HEIGHT = 600
        
    class Fonts(object):
        
        MAIN_TABS_FONT = {'family':'Helvetica', 'size':14, 'weight':'bold'}
        
    
    class Names(object):
        
        TITLE = 'Asset Creator Tool'
        
        MAIN_NOTEBOOK_START_TAB = 'Start'
        MAIN_NOTEBOOK_SET_TAB = 'Set'
        MAIN_NOTEBOOK_PLAYER_ACTION_TAB = 'Player Action'
        MAIN_NOTEBOOK_ATTACK_ACTION_TAB = 'Attack Action'   

    
    def __init__(self):
        
        WN = AssetCreatorTool.Names
        C = AssetCreatorTool.Constants
        
        self.root = tk.Tk()
        self.root.title(WN.TITLE)
        self.root.protocol('WM_DELETE_WINDOW', self.exit)
        self.main_frame = tk.Frame(self.root, width = C.WINDOW_WIDTH,height = C.WINDOW_HEIGHT)
        self.main_frame.pack()
        
        
        self.create_main_notebook(self.main_frame)
        print "GUI initialized"
        
    def exit(self):
        print "GUI exiting"
        self.root.quit()
        self.root = None
    
    def create_main_notebook(self,parent):
        
        WN = AssetCreatorTool.Names
        C = AssetCreatorTool.Constants
        F = AssetCreatorTool.Fonts
        
        frame_font = tkFont.Font(self.root,family = F.MAIN_TABS_FONT['family'],size = F.MAIN_TABS_FONT['size'])
        w = C.WINDOW_WIDTH
        h = C.WINDOW_HEIGHT
        self.main_notebook = ttk.Notebook(parent,width = w,height = h)
        n = self.main_notebook
        
        f1 = ttk.Frame(self.main_notebook)
        f2 = ttk.Frame(self.main_notebook)
        f3 = ttk.Frame(self.main_notebook)
        f4 = ttk.Frame(self.main_notebook)
        
        n.add(f1,text= WN.MAIN_NOTEBOOK_START_TAB)
        n.add(f2,text= WN.MAIN_NOTEBOOK_SET_TAB)
        n.add(f3,text= WN.MAIN_NOTEBOOK_PLAYER_ACTION_TAB)
        n.add(f4,text= WN.MAIN_NOTEBOOK_ATTACK_ACTION_TAB)
        
        n.pack()        
        
    def run(self):
        
        print "GUI started"
        while (self.root != None):
            self.root.update()