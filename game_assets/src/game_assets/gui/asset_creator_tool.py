import Tkinter as tk
import tkFont
import ttk
from game_assets.gui.properties import *

class SelectionWidget(ttk.Frame):
    
    def __init__(self,parent,combo_label_text,choices = [],select_cb = None,add_cb = None,delete_cb = None):
        
        ttk.Frame.__init__(self, parent)
        self.combo_label_text = combo_label_text
        self.choices = choices
        
        self.setup()
        
    def setup(self):  
                
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        F = GUIProperties.Fonts   
        
        # set selection widgets
        self.select_label = ttk.Label(self,text=self.combo_label_text,padding = (2,4),
                                      font = F.SET_SELECTION_LABEL)
        self.select_combo = ttk.Combobox(self,values = self.choices,
                                         font = F.SET_COMBO_BOX,justify = tk.CENTER)
        self.select_combo.state(['!disabled', 'readonly'])
        
        # selecting widgets
        if len(self.choices)>0:
            self.select_combo.current(0)  
        
        button_style = ttk.Style()
        button_style.configure('SelectionWidget.TButton',font = F.SET_BUTTON)
        self.add_button = ttk.Button(self,text = 'Add',style = 'SelectionWidget.TButton')
        self.rename_button = ttk.Button(self,text = 'Rename',style = 'SelectionWidget.TButton')
        self.delete_button = ttk.Button(self,text = 'Delete',style = 'SelectionWidget.TButton')        
        
        self.select_label.pack(side=tk.LEFT,padx = 2,pady = 4)
        self.select_combo.pack(side = tk.LEFT,padx = 2,pady = 4) 
        self.add_button.pack(side = tk.LEFT,padx = 4,pady = 4)
        self.rename_button.pack(side = tk.LEFT,padx = 4,pady = 4)
        self.delete_button.pack(side = tk.LEFT,padx = 4,pady = 4)
        
        self.pack(expand = True,fill = tk.BOTH)     
        
class ActionsEditWidget(ttk.Frame):
    
    def __init__(self,parent,choices):
        
        ttk.Frame.__init__(self, parent)
        self.choices = choices
        
        self.setup()
        self.pack(fill=tk.BOTH,expand = True)
        
    def setup(self):
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        F = GUIProperties.Fonts        
        w = C.WINDOW_WIDTH
        h = C.WINDOW_HEIGHT
        
        # selection and editing widgets
        self.selection_widget = SelectionWidget(self,'Select Action',self.choices)     
        self.action_nb = ttk.Notebook(self,width = w,height = h)        
        
        # action frames (player, attack)
        self.action_frame = ttk.Frame(self.action_nb) 
        self.attack_frame = ttk.Frame(self.action_nb)        
        self.action_nb.add(self.action_frame,text= WN.SET_NB_ACTION_FRAME)
        self.action_nb.add(self.attack_frame,text= WN.SET_NB_ATTACK_FRAME)
        
        self.selection_widget.pack(side = tk.TOP,expand = True,padx = 4,pady = 4,fill=tk.X)
        self.action_nb.pack(side = tk.BOTTOM,expand = True,padx = 4,pady = 4)
        

class AssetSetWidget(ttk.Frame):
    
    def __init__(self,parent):
        
        ttk.Frame.__init__(self, parent)
                
        self.setup()        
        
        self.pack(fill=tk.BOTH,expand = True)

        
    def setup(self):
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        F = GUIProperties.Fonts
        
        w = C.WINDOW_WIDTH
        h = C.WINDOW_HEIGHT
    
        # frames        
        frame_style = ttk.Style()
        frame_style.configure('Edit.TFrame', background='#000000')
        self.selection_frame = ttk.Frame(self,borderwidth = 2,style = 'Edit.TFrame')
        self.editing_frame = ttk.LabelFrame(self,borderwidth = 2,text= 'Actions') 
        
        self.set_items = {'set1':object(),'set2':object(),'set3':object()}
        self.management_widget = SelectionWidget(self.selection_frame,'Select Set',self.set_items.keys())        
        
        # action editing widgets
        self.action_items = {'action1':object(),'action2':object(),'action3':object(),'action4':object()}
        self.action_editing_widget = ActionsEditWidget(self.editing_frame,self.action_items.keys())
        
        # packing parent frames
        self.selection_frame.pack(side = tk.TOP,pady = 4,padx = 4,expand=True,fill = tk.X)
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