import Tkinter as tk
import tkFont
import ttk
from game_assets.gui.properties import *

class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        return

class SpriteSheetWidget(ttk.Frame):
    
    def __init__(self,parent):
        
        ttk.Frame.__init__(self, parent)
        ttk.file_path = ''
        
        self.setup()
        
    def setup(self):
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        F = GUIProperties.Fonts
        
        self.configure(borderwidth = 2,relief = tk.GROOVE)
        
        # image file controls
        self.open_image_button = ttk.Button(self,text = 'Open File')
        self.file_path_label = ttk.Label(self,text = 'Image Path')
        self.path_label = ttk.Label(self, text = '/',font = F.COLLECTION_INFO,
                                    background = "#fff",relief = 'sunken',padding = (2,4))
        
        # image breakdown
        self.columns_label = ttk.Label(self,text = 'cols')
        self.columns_spin = tk.Spinbox(self,from_ = 0,to = 0)
        self.rows_label = ttk.Label(self,text = 'rows')
        self.rows_spin = tk.Spinbox(self,from_ = 0,to = 0)
        self.size_label = ttk.Label(self,text = 'size')
        self.size_info_label = ttk.Label(self,font = F.COLLECTION_INFO,
                                    background = "#fff",relief = 'sunken',text = '0x0')
        
        # image display
        self.sprite_canvas = tk.Canvas(self,width = 200,height = 100)
        
        self.open_image_button.grid(column = 0,row = 0,padx = 4,pady = 2)
        self.file_path_label.grid(column = 1,row = 0,padx = 2,pady = 2)
        self.path_label.grid(column = 2,row = 0,columnspan = 4, padx = 2,pady = 2)
        
        self.columns_label.grid(column = 0,row = 1,padx = 2,pady = 2)
        self.columns_spin.grid(column = 1,row = 1,padx = 2,pady = 2)
        self.rows_label.grid(column = 2,row = 1,padx = 2,pady = 2)
        self.rows_spin.grid(column = 3,row = 1,padx = 2,pady = 2)   
        self.size_label.grid(column = 4,row = 1,padx = 2,pady = 2)
        self.size_info_label.grid(column = 5,row = 1,padx = 2,pady = 2)
        
        self.sprite_canvas.grid(column = 0,row = 2,columnspan = 6,rowspan = 2)   
        
class AnimationWidget(ttk.Frame):
    
    def __init__(self,parent):
        
        ttk.Frame.__init__(self, parent)     
        self.setup()
        
    def setup(self):
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        F = GUIProperties.Fonts        
        w = C.WINDOW_WIDTH
        h = int(C.WINDOW_HEIGHT*0.8)
        sframew = int(0.8*w)
        sframeh = int(0.4*h)
        
        # creating notebook
        self.left_right_nb = ttk.Notebook(self,width = w, height = h)
        self.right_frame = ttk.Frame(self.left_right_nb,width = sframew,height = sframeh)
        self.left_frame = ttk.Frame(self.left_right_nb,width = sframew,height = sframeh)
        
        # sprite sheet widget frames
        self.right_sprites_frame = VerticalScrolledFrame(self.right_frame)
        self.right_sprites_frame.configure(relief = tk.SUNKEN,borderwidth = 1)
        self.left_sprites_frame = VerticalScrolledFrame(self.left_frame)  
        self.left_sprites_frame.configure(relief = tk.SUNKEN,borderwidth = 1)     
        
        
        # creating sprite sheet widgets
        num_sprite_widgets = 3
        for i in range(0,3):
             
            sw = SpriteSheetWidget(self.right_sprites_frame.interior)
            sw.pack(fill = tk.X)
             
        #endfor
        self.right_sprites_frame.configure(width = sframew,height = sframeh)
        
        
        self.left_right_nb.add(self.right_frame,text = 'Right')
        self.left_right_nb.add(self.left_frame,text = 'Left')
        self.right_sprites_frame.pack(fill = tk.BOTH)
        self.left_sprites_frame.pack(fill = tk.BOTH)
        
        self.left_right_nb.pack()        


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
        
        #self.pack(expand = True,fill = tk.BOTH)     
        
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
        self.animation_frame = AnimationWidget(self.action_nb)
        self.collision_frame = ttk.Frame(self.action_nb)
        self.attack_frame = ttk.Frame(self.action_nb)        
        self.action_nb.add(self.animation_frame,text= WN.ACTION_NB_ANIMATION_FRAME)
        self.action_nb.add(self.collision_frame,text= WN.ACTION_NB_COLLISION_FRAME)
        self.action_nb.add(self.attack_frame,text= WN.ACTION_NB_ATTACK_FRAME)
        
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
        self.management_widget.pack(expand = True,fill = tk.BOTH)      
        
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