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

    

class SelectionWidget(ttk.Frame):
    
    def __init__(self,parent,combo_label_text,choices = [],select_cb = None,add_cb = None,delete_cb = None,rename_cb = None):
        
        ttk.Frame.__init__(self, parent)
        self.add_button_callback = add_cb 
        self.delete_button_callback = delete_cb 
        self.rename_button_callback = rename_cb 
        self.combo_label_text = combo_label_text
        self.choices = choices
        self.file_name = ''
        
        self.setup()
        
    def setup(self):  
                
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        F = GUIProperties.Fonts   
        
        # set selection widgets
        self.select_label = ttk.Label(self,text=self.combo_label_text,padding = (2,4),
                                      font = F.SET_SELECTION_LABEL)
        self.entry_var = tk.StringVar()
        #self.entry_var.set(0)
        self.select_combo = ttk.Combobox(self,values = self.choices,textvariable = self.entry_var,
                                         font = F.SET_COMBO_BOX,justify = tk.CENTER)
        self.select_combo.state(['!disabled', 'readonly'])
        self.select_combo.items = []
        
        # selecting widgets
#         if len(self.choices)>0:
#             self.select_combo.current(0)  
        
        # creating buttons
        button_style = ttk.Style()
        button_style.configure('SelectionWidget.TButton',font = F.SET_BUTTON)
        self.add_button = ttk.Button(self,text = 'Add',style = 'SelectionWidget.TButton',command = self.add_item)
        self.rename_button = ttk.Button(self,text = 'Rename',style = 'SelectionWidget.TButton',command = self.rename_item)
        self.delete_button = ttk.Button(self,text = 'Delete',style = 'SelectionWidget.TButton',command = self.delete_item)                 
        
        
        self.select_label.pack(side=tk.LEFT,padx = 2,pady = 4)
        self.select_combo.pack(side = tk.LEFT,padx = 2,pady = 4) 
        self.add_button.pack(side = tk.LEFT,padx = 4,pady = 4)
        self.rename_button.pack(side = tk.LEFT,padx = 4,pady = 4)
        self.delete_button.pack(side = tk.LEFT,padx = 4,pady = 4)       

        
    def add_item(self):
        
        item = self.entry_var.get()
        new_item = None
        if self.add_button_callback != None:
            
            new_item = str(self.add_button_callback(item))
            
        #endif
        
        if new_item != None:
                        
            self.select_combo.items.append(new_item)
            self.select_combo['values'] = self.select_combo.items
            self.select_combo.current(self.select_combo.items.index(new_item, 0))
         #endif 
         
    def set_items(self,items):
        
        self.select_combo.items =[]
        for i in items:
            self.select_combo.items.append(str(i))
            
        #endfor
        
        self.select_combo['values'] = self.select_combo.items
          
        
    def delete_item(self):
        
        item = self.entry_var.get()
        
        index = self.select_combo.items.index(item,0 )
        del self.select_combo.items[index]
        self.select_combo['values'] = self.select_combo.items
        
        if self.delete_button_callback != None:
            
            self.delete_button_callback(item)
        #endif 
        
        if len(self.select_combo.items) == 0:
            
            self.select_combo.set('')
            
        else:                
            
            if len(self.select_combo.items) > index:
                self.select_combo.current(index)
                
            else :
                self.select_combo.current(index-1)
            
            #endif
            
       #endif
        
    def rename_item(self):
        
        item = self.entry_var.get()
        new_item = None
        if self.rename_button_callback != None:
            
            self.rename_button_callback(item)
        #endif
        
        if new_item != None:
                        
            self.select_combo.delete(item)
            self.select_combo.insert(tk.END,new_item)
        #endif 
        
        