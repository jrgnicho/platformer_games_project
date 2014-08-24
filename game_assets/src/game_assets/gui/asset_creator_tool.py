import Tkinter as tk
import tkFont
import ttk
from game_assets.gui.properties import *

class AssetSetWidget(object,ttk.Frame):
    
    def __init__(self,parent):
        
        ttk.Frame.__init__(self, parent)
        
        self.sets = {'set1':object(),'set2':object,'set3':object}
        
        self.setup()        
        
        self.pack(fill=tk.BOTH,expand = True)

        
    def setup(self):
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        F = GUIProperties.Fonts
        
        w = C.WINDOW_WIDTH
        h = C.WINDOW_HEIGHT
    
        # frames
        self.selection_frame = ttk.Frame(self,borderwidth = 2)
        self.editing_frame = ttk.Frame(self,borderwidth = 2) 
        
        # set selection widgets
        self.select_label = ttk.Label(self.selection_frame,text='Select Set',padding = (2,4),
                                      font = F.SET_SELECTION_LABEL)
        self.select_combo = ttk.Combobox(self.selection_frame,values = self.sets.keys(),
                                         font = F.SET_COMBO_BOX)
        self.select_label.pack(side=tk.LEFT)
        self.select_combo.pack(side = tk.LEFT)       
        
        
        # action editing widgets
        self.set_nb = ttk.Notebook(self.editing_frame,width = w,height = h)
        
        # action frames (player, attack)
        self.pa_frame = ttk.Frame(self.set_nb) 
        self.aa_frame = ttk.Frame(self.set_nb)
         
        self.set_nb.add(self.pa_frame,text= WN.COLLECTION_NB_PLAYER_ACTION_FRAME)
        self.set_nb.add(self.aa_frame,text= WN.COLLECTION_NB_ATTACK_ACTION_FRAME)
        self.set_nb.pack(fill=tk.BOTH,expand = True,side = tk.LEFT)
        
        # packing parent frames
        self.selection_frame.pack(side = tk.TOP,pady = 4,padx = 4)
        self.editing_frame.pack(side = tk.BOTTOM ,pady = 4,padx = 4,expand=True)

class AssetCreatorTool(object):
    
    TK_ROOT = tk.Tk()      

    
    def __init__(self):
        
        self.root = self.TK_ROOT
        self.setup()
        
    def setup(self):
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants        
        F = GUIProperties.Fonts
        
        self.root.title(WN.TITLE)
        self.root.protocol('WM_DELETE_WINDOW', self.exit)
        self.main_frame = ttk.Frame(self.root, width = C.WINDOW_WIDTH,height = C.WINDOW_HEIGHT)
        self.main_frame.pack()
        
        # root style
        self.root_style = ttk.Style()
        self.root_style.configure(".", font = F.MAIN_TABS)
        
        # internal widgets
        self.main_notebook = None
        self.start_frame = None
        self.collection_frame = None
        self.sets_frame = None
        self.sets_widget = None
        
        
        self.create_main_notebook(self.main_frame)
        self.create_collection_frame(self.collection_frame)
        self.create_sets_widget(self.sets_frame)
        
        print "GUI initialized"
        
    def exit(self):
        print "GUI exiting"
        self.root.quit()
        self.root = None
    
    def create_main_notebook(self,parent):
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants        
        F = GUIProperties.Fonts
        
        w = C.WINDOW_WIDTH
        h = C.WINDOW_HEIGHT
        self.main_notebook = ttk.Notebook(parent,width = w,height = h)
        n = self.main_notebook
            
        self.start_frame = ttk.Frame(n)
        self.collection_frame = ttk.Frame(n)
        
        n.add(self.start_frame,text =WN.MAIN_NB_START_FRAME)
        n.add(self.collection_frame,text= WN.MAIN_NB_COLLECTION_FRAME)
                
        n.pack()     
        
    def create_collection_frame(self,parent):  
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        F = GUIProperties.Fonts
        
        w = C.WINDOW_WIDTH
        h = C.WINDOW_HEIGHT
        
        label_frame_style = ttk.Style()
        label_frame_style.configure('Sets.TButton', font = F.SET_LABEL_FRAME)
        self.details_frame = ttk.Frame(parent)     
        self.sets_frame = ttk.LabelFrame(parent,borderwidth = 2,text = 'Set',style = 'Sets.TButton')
        
        # details frame
        label_name = ttk.Label(self.details_frame,text=WN.COLLECTION_FRAME_LABEL,font = F.COLLECTION_LABELS,
                               padding = (2,4))
        label_name_info = ttk.Label(self.details_frame, text = 'DefaultCollection',font = F.COLLECTION_INFO,
                                    background = "#fff",relief = 'sunken',padding = (2,4))
        label_path = ttk.Label(self.details_frame,text = 'File path',font = F.COLLECTION_LABELS,padding = (2,4))
        label_path_info = ttk.Label(self.details_frame, text = '/no/path/designated',font = F.COLLECTION_INFO,
                                    background = "#fff",relief = 'sunken',padding = (2,4))
        
        label_name.grid(row = 0,column = 0,padx = 6,pady=2,sticky='W')
        label_name_info.grid(row = 0,column = 1,sticky='W')
        label_path.grid(row = 1, column = 0,padx = 6,pady=2,sticky='W')
        label_path_info.grid(row = 1, column = 1,sticky='W')
       
                
        self.details_frame.pack(fill=tk.BOTH,side = tk.TOP)
        self.sets_frame.pack(fill = tk.BOTH,side = tk.BOTTOM,expand= True,pady = 4)
        
    def create_sets_widget(self,parent):
        
        self.sets_widget = AssetSetWidget(parent)
        
    def run(self):
        
        print "GUI started"
        while (self.root != None):
            self.root.update()