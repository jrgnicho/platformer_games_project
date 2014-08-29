import Tkinter as tk
import tkFont
import ttk
from game_assets.gui.properties import *
from game_assets.gui.general_widgets import *


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