import Tkinter as tk
import tkFont
import ttk
import tkFileDialog
import pygame
from PIL import Image, ImageTk
import os
from pygame.sprite import Sprite
from game_assets.gui.properties import *
from game_assets.gui.general_widgets import *


class SpriteSheetWidget(ttk.Frame):
    
    def __init__(self,parent):
        
        ttk.Frame.__init__(self, parent)
        self.file_path = ''
        self.file_name = ''
        self.pygame_image = None
        self.tk_image = None
        self.size = (0,0)
        
        
        self.setup()
        
    def setup(self):
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        F = GUIProperties.Fonts
        
        style = ttk.Style()
        style.configure('SpriteWidget.TFrame', background = "#0066ff")
        self.configure(borderwidth = 2,relief = tk.GROOVE,style = 'SpriteWidget.TFrame')
        
        # image file controls
        self.file_controls_frame = ttk.Frame(self)
        self.open_image_button = ttk.Button(self.file_controls_frame,text = 'Open File',command = self.open_file_callback)
        self.file_path_label = ttk.Label(self.file_controls_frame,text = 'Image Path')
        self.path_label = ttk.Label(self.file_controls_frame, text = '/',font = F.COLLECTION_INFO,
                                    background = "#fff",relief = 'sunken',padding = (2,4),width = 100)
        
        self.open_image_button.pack(side = tk.LEFT,padx = 4)
        self.file_path_label.pack(side = tk.LEFT,padx = 2)
        self.path_label.pack(side = tk.LEFT,padx = 2)
        
        # image breakdown
        self.props_frame = ttk.Frame(self)
        self.columns_label = ttk.Label(self.props_frame ,text = 'cols',width = 6,anchor = tk.CENTER)
        self.columns_spin = tk.Spinbox(self.props_frame, from_ = 1,to = 99,width = 2,font = F.SPRITE_WIDGET_SPIN,
                                       command = self.update_image,state = tk.DISABLED)
        self.rows_label = ttk.Label(self.props_frame ,text = 'rows',width = 6,anchor = tk.CENTER)
        self.rows_spin = tk.Spinbox(self.props_frame ,from_ = 1,to = 99,width = 2,font = F.SPRITE_WIDGET_SPIN,
                                    command = self.update_image,state = tk.DISABLED)
        
        self.scale_label = ttk.Label(self.props_frame,text = 'scale',width = 6,anchor = tk.CENTER)        
        self.scale_entry = ttk.Entry(self.props_frame,validate = tk.ALL,
                                         validatecommand = (self.register(self.validate_entry), '%d', '%i', '%S'),
                                         width = 4,font = F.SPRITE_WIDGET_SPIN)
        self.scale_entry.insert(0, '1')
        
        self.size_label = ttk.Label(self.props_frame ,text = 'size',width = 5,anchor = tk.CENTER)
        self.size_info_label = ttk.Label(self.props_frame ,font = F.COLLECTION_INFO,width = 5,
                                    background = "#fff",relief = 'sunken',text = '0x0',anchor = tk.CENTER)
        
        
        # disabling sprite control widgets
        self.enable_sprite_widgets(False)
        
        self.columns_label.pack(side = tk.LEFT,padx = 2)
        self.columns_spin.pack(side = tk.LEFT,padx = 2)
        self.rows_label.pack(side = tk.LEFT,padx = 2)
        self.rows_spin.pack(side = tk.LEFT,padx = 2)
        self.scale_label.pack(side = tk.LEFT,padx = 2)
        self.scale_entry.pack(side = tk.LEFT,padx = 2)
        self.size_label.pack(side = tk.LEFT,padx = 2)
        self.size_info_label.pack(side = tk.LEFT,padx = 2)    
        
        # sprite canvas
        self.sprite_canvas = tk.Canvas(self,width = 200,height = 100)  
        
        self.file_controls_frame.pack(fill = tk.X,pady = 2)
        self.props_frame.pack(fill = tk.X,pady = 2)
        self.sprite_canvas.pack(fill = tk.X,pady = 2)
        
        # image display
        w = int(self.sprite_canvas['width'])
        h = int(self.sprite_canvas['height'])
        surf = pygame.Surface((w,h))
        surf.fill((240,240,255))
        image_str = pygame.image.tostring(surf,'RGBA')
        self.tk_image = ImageTk.PhotoImage(Image.frombuffer('RGBA',(w,h),image_str,'raw','RGBA',0,1), (w,h))
        self.image_id = self.sprite_canvas.create_image(w/2,h/2,image = self.tk_image)
        
    def enable_sprite_widgets(self,enable = True):
        
        state = tk.NORMAL if enable else tk.DISABLED
        self.columns_spin.config(state = state)
        self.rows_spin.config(state = state)
        self.scale_entry.config(state = state)
        
    def open_file_callback(self):
        
        #p =   tkFileDialog.askopenfilename(filetypes = [('Image Files','*.png,*.bmp,*.jpg,*.gif')])
        p =   tkFileDialog.askopenfilename(filetypes = GUIProperties.IMAGE_FORMATS)
        
        if (p != None) and (p != ''):
            self.file_path = p
            self.file_name = os.path.basename(self.file_path)
            self.path_label.configure(text = self.file_name)      
            
            self.enable_sprite_widgets(True)
            self.open_image()
            self.update_image()
            
    def update_image(self):
        
        CL = GUIProperties.PG_Colors
        
        cols = int(self.columns_spin.get())
        rows = int(self.rows_spin.get())
        
        # individual sprite size
        w = self.pygame_image.get_width()
        h = self.pygame_image.get_height()
        sw = w/cols
        sh = h/rows
        
        self.cell_image = self.pygame_image.copy()
        for r in range(0,rows):
            
            pygame.draw.line(self.cell_image,CL.RED,(0,r*sh),(w,r*sh))
            pygame.draw.line(self.cell_image,CL.RED,(0,(r+1)*sh-1),(w,(r+1)*sh-1))
            for c in range(1,cols+1):                
        
                pygame.draw.line(self.cell_image,CL.RED,(c*sw-1,r*sh),(c*sw-1,(r+1)*sh))                
            #endfor
        #endfor
        
        self.draw_image(self.cell_image)
        
    def open_image(self):
        
        CL = GUIProperties.PG_Colors
        
        self.pygame_image = pygame.image.load(self.file_path).convert()
        self.pygame_image.set_colorkey(CL.BLACK)
        w= self.pygame_image.get_width()
        h = self.pygame_image.get_height()
        self.size = (w,h)

        return self.pygame_image
        
    def draw_image(self,surf):
        
        w = surf.get_width()
        h = surf.get_height()
        image_str = pygame.image.tostring(surf,'RGBA')
        self.tk_image = ImageTk.PhotoImage(Image.frombuffer('RGBA',(w,h),image_str,'raw','RGBA',0,1),
                                           (w,h))
        self.sprite_canvas.itemconfig(self.image_id, image = self.tk_image)  
        ch = int(self.sprite_canvas['height'])
        self.sprite_canvas.coords(self.image_id,(w/2,h/2 + ch/4))  
        
        
    def validate_entry(self,why,where,val):
        
        entry = str(val)
        
        return entry.isdigit() or entry.find('.')>=0
    
class AnimationsWidget(ttk.Frame):
    
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
        self.right_frame = AnimationConfigWidget(self.left_right_nb)
        self.left_frame = AnimationConfigWidget(self.left_right_nb)
        
        
        self.left_right_nb.add(self.right_frame,text = 'Right')
        self.left_right_nb.add(self.left_frame,text = 'Left')
        self.left_right_nb.pack()       
         
        
class AnimationConfigWidget(ttk.Frame):
    
    def __init__(self,parent):
        
        
        ttk.Frame.__init__(self, parent)   
        self.sprite_widgets_list= []
        self.setup()
        
        
    def setup(self):
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        F = GUIProperties.Fonts        
        w = C.WINDOW_WIDTH
        h = int(C.WINDOW_HEIGHT*0.8)
        sframew = int(0.8*w)
        sframeh = int(0.4*h)
        
        # configure size
        self.configure(width = sframew,height = sframeh)
        
        # selection widget
        self.selection_widget = SelectionWidget(self,'Sprites',add_cb = self.add_sprite_widget,
                                                delete_cb = self.remove_sprite_widget)
        self.selection_widget.rename_button.pack_forget()
        
        # sprite sheet widget frames
        self.sprites_frame = VerticalScrolledFrame(self)
        self.sprites_frame.configure(relief = tk.SUNKEN,borderwidth = 1)          
        self.sprites_frame.configure(width = sframew,height = sframeh)         
    
        self.selection_widget.pack(fill = tk.BOTH)   
        self.sprites_frame.pack(fill = tk.BOTH)
        
    def add_sprite_widget(self,selection_str):
        
        sw = SpriteSheetWidget(self.sprites_frame.interior)
        sw.pack(fill = tk.X)
        key = len(self.sprite_widgets_list)+1        
        self.sprite_widgets_list.append(sw)
        
        return key
        
    def remove_sprite_widget(self,selection_str):
        
        index = int(selection_str)-1
        if len(self.sprite_widgets_list) > index:
            self.sprite_widgets_list[index].pack_forget()
            del self.sprite_widgets_list[index]
            
            # resetting items
            self.selection_widget.set_items(range(1,len(self.sprite_widgets_list) + 1))
            
            