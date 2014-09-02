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

class ImageCanvas(tk.Canvas):    
    
    
    def __init__(self,parent,width,height):
        
        tk.Canvas.__init__(self, parent,width = width,height = height)
        self.setup()
        
    def setup(self):
        
        CL = GUIProperties.PG_Colors
        
        w = int(self['width'])
        h = int(self['height'])
        surf = pygame.Surface((w,h))
        surf.fill(CL.LIGHT_BLUE)
        image_str = pygame.image.tostring(surf,'RGBA')
        self.tk_image = ImageTk.PhotoImage(Image.frombuffer('RGBA',(w,h),image_str,'raw','RGBA',0,1), (w,h))
        self.image_id = self.create_image(w/2,h/2,image = self.tk_image)
        
    def draw(self,surf):
        
        w = surf.get_width()
        h = surf.get_height()
        image_str = pygame.image.tostring(surf,'RGBA')
        self.tk_image = ImageTk.PhotoImage(Image.frombuffer('RGBA',(w,h),image_str,'raw','RGBA',0,1),
                                           (w,h))
        self.itemconfig(self.image_id, image = self.tk_image)  
        ch = int(self['height'])
        self.coords(self.image_id,(w/2,ch/2))  

class SpriteAnimationWidget(ttk.Frame):    

    
    def __init__(self,parent):
        
        ttk.Frame.__init__(self,parent)
        self.sprites = pygame.sprite.Group()
        self.setup()
        
    def setup(self):
        
        F = GUIProperties.Fonts    
        C = GUIProperties.Constants
        
        # play controls
        self.play_controls_frame = ttk.Frame(self)
        
        # play rate
        self.play_rate_frame = ttk.Frame(self.play_controls_frame)
        self.play_rate_var = tk.IntVar(value = 100)
        self.play_rate_label = ttk.Label(self.play_rate_frame,text = 'Rate(ms)')
        self.play_rate_spin = tk.Spinbox(self.play_rate_frame,from_ = 40,to = 200,justify = tk.CENTER, 
                                         textvariable = self.play_rate_var,                                        
                                          font = F.SPRITE_WIDGET_SPIN,state = tk.DISABLED)
        self.play_rate_label.pack(side = tk.LEFT,padx = 2)
        self.play_rate_spin.pack(side = tk.LEFT,padx = 2)
        
        # play buttons
        self.play_button = ttk.Button(self.play_controls_frame,text = 'Play')
        self.stop_button = ttk.Button(self.play_controls_frame,text = 'Stop')
        
        
        # frame selection
        self.selection_frame = ttk.Frame(self.play_controls_frame)
        self.selection_var = tk.IntVar(value = 0)
        self.selection_label = ttk.Label(self.selection_frame,text = "Frame Index")
        self.selection_var = tk.IntVar(value = 0)
        self.selection_spin = tk.Spinbox(self.selection_frame,justify = tk.CENTER, 
                                         textvariable = self.selection_var,
                                         font = F.SPRITE_WIDGET_SPIN,state = tk.DISABLED)
        
        self.selection_label.pack(side = tk.LEFT,padx = 2)
        self.selection_spin.pack(side = tk.LEFT,padx = 2)
        
        # animation canvas
        self.animation_canvas = ImageCanvas(self,width = C.ANIMATION_CANVAS_WIDTH,height = C.ANIMATION_CANVAS_HEIGHT)
        
        # play controls layout
        self.play_rate_frame.pack(fill = tk.X,pady = 2)
        self.play_button.pack(fill = tk.X,pady = 2)
        self.stop_button.pack(fill = tk.X,pady = 2)
        self.selection_frame.pack(fill = tk.X,pady = 4)
        
        # top layout
        self.play_controls_frame.pack(fill = tk.BOTH,side = tk.LEFT)
        self.animation_canvas.pack(fill = tk.BOTH,side = tk.LEFT,padx = 10)
        


class SpriteSheetWidget(ttk.Frame):
    
    def __init__(self,parent):
        
        ttk.Frame.__init__(self, parent)
        self.file_path = ''
        self.file_name = ''
        self.pg_original_image = None
        self.tk_image = None
        self.pg_sprites_image = None
        self.sprites = pygame.sprite.Group()
        
        
        self.setup()
        
    def setup(self):
        
        WN = GUIProperties.Names
        C = GUIProperties.Constants
        CL = GUIProperties.PG_Colors
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
                                       command = self.update_sprites,state = tk.DISABLED)
        self.rows_label = ttk.Label(self.props_frame ,text = 'rows',width = 6,anchor = tk.CENTER)
        self.rows_spin = tk.Spinbox(self.props_frame ,from_ = 1,to = 99,width = 2,font = F.SPRITE_WIDGET_SPIN,
                                    command = self.update_sprites,state = tk.DISABLED)
        
        # scale x widgets
        self.scalex_var = tk.DoubleVar()
        self.scalex_label = ttk.Label(self.props_frame,text = 'scale x',width = 6,anchor = tk.CENTER)        
        self.scalex_entry = ttk.Entry(self.props_frame,validate = tk.ALL,
                                         validatecommand = (self.register(self.validate_entry), '%d', '%i', '%S'),
                                         width = 4,font = F.SPRITE_WIDGET_SPIN,
                                         textvariable = self.scalex_var)
        self.scalex_entry.bind('<Return>',lambda evnt: self.update_sprites())
        self.scalex_var.set(1.0)
        
        # scale y widgets
        self.scaley_var = tk.DoubleVar()
        self.scaley_label = ttk.Label(self.props_frame,text = 'scale y',width = 6,anchor = tk.CENTER)
        self.scaley_entry = ttk.Entry(self.props_frame,validate = tk.ALL,
                                      validatecommand = (self.register(self.validate_entry),'%d','%i','%S'),
                                      width = 4,font = F.SPRITE_WIDGET_SPIN,
                                      textvariable = self.scaley_var)
        self.scaley_entry.bind('<Return>',lambda evnt: self.update_sprites())
        self.scaley_var.set(1.0)
        
        # flip x/y check buttons
        self.flipx_check_var = tk.BooleanVar()
        self.flipx_check_button = ttk.Checkbutton(self.props_frame,text = 'Flip x',variable = self.flipx_check_var,
                                                  command = self.update_sprites)
        self.flipx_check_var.set(False)
        
        self.flipy_check_var= tk.BooleanVar(value = False)
        self.flipy_check_button = ttk.Checkbutton(self.props_frame,text = 'Flip y',variable = self.flipy_check_var,
                                                  command = self.update_sprites)
        
        self.size_label = ttk.Label(self.props_frame ,text = 'size',width = 5,anchor = tk.CENTER)
        self.size_info_label = ttk.Label(self.props_frame ,font = F.COLLECTION_INFO,width = 8,
                                    background = "#fff",relief = 'sunken',text = '0x0',anchor = tk.CENTER)
        
        
        
        # disabling sprite control widgets
        self.enable_sprite_widgets(False)
        
        self.columns_label.pack(side = tk.LEFT,padx = 2)
        self.columns_spin.pack(side = tk.LEFT,padx = 2)
        self.rows_label.pack(side = tk.LEFT,padx = 2)
        self.rows_spin.pack(side = tk.LEFT,padx = 2)
        self.scalex_label.pack(side = tk.LEFT,padx = 2)
        self.scalex_entry.pack(side = tk.LEFT,padx = 2)
        self.scaley_label.pack(side = tk.LEFT,padx = 2)
        self.scaley_entry.pack(side = tk.LEFT,padx = 2)
        self.flipx_check_button.pack(side = tk.LEFT,padx =2)
        self.flipy_check_button.pack(side = tk.LEFT,padx =2)
        self.size_label.pack(side = tk.LEFT,padx = 2)
        self.size_info_label.pack(side = tk.LEFT,padx = 2)    
        
        # sprite canvas
        self.sprite_canvas = ImageCanvas(self,width = C.SPRITE_SHEET_CANVAS_WIDTH,height = C.SPRITE_SHEET_CANVAS_HEIGHT) 
        
        self.file_controls_frame.pack(fill = tk.X,pady = 2)
        self.props_frame.pack(fill = tk.X,pady = 2)
        self.sprite_canvas.pack(fill = tk.X,pady = 2)
        
        
    def enable_sprite_widgets(self,enable = True):
        
        state = tk.NORMAL if enable else tk.DISABLED
        self.columns_spin.config(state = state)
        self.rows_spin.config(state = state)
        self.scalex_entry.config(state = state)
        self.scaley_entry.config(state = state)
        
    def open_file_callback(self):
        
        p =   tkFileDialog.askopenfilename(filetypes = GUIProperties.IMAGE_FORMATS)
        
        if (p != None) and (p != ''):
            self.file_path = p
            self.file_name = os.path.basename(self.file_path)
            self.path_label.configure(text = self.file_name)      
            
            self.enable_sprite_widgets(True)
            self.open_image()
            self.update_sprites()
            self.update_indicator_widgets()
            
    def generate_sprites(self):
        
        CL = GUIProperties.PG_Colors
        
        # resetting sprite group
        self.sprites.empty()
        
        # sprite breakdown
        cols = int(self.columns_spin.get())
        rows = int(self.rows_spin.get())
        
        # individual sprite size
        w = int(self.pg_original_image.get_width()*self.scalex_var.get())
        h = int(self.pg_original_image.get_height()*self.scaley_var.get())
        sw = w/cols
        sh = h/rows
        
        scaled_sprites_image = self.scale_image(self.pg_original_image, w, h)
        self.pg_sprites_image = pygame.Surface([w,h]).convert()
        
        for j in range(0,rows):            
            for i in range(0,cols):                
                x = i * sw
                y = j * sh
                
                # extracting image
                image = pygame.Surface([sw, sh]).convert()
                image.blit(scaled_sprites_image,(0,0),(x,y,sw,sh))
                #image.set_colorkey(CL.BLACK)
                
                # fliping image         
                image = pygame.transform.flip(image,self.flipx_check_var.get(),self.flipy_check_var.get())
                sprite  = pygame.sprite.Sprite()
                sprite.image = image
                sprite.rect = image.get_rect()
                self.sprites.add(sprite) 
                
                # drawing on sprites image
                self.pg_sprites_image.blit(image,(x,y),(0,0,sw,sh))
            #endfor
        #endfor
        
        self.pg_sprites_image.set_colorkey(CL.BLACK)
        
            
    def update_sprites(self):
        
        CL = GUIProperties.PG_Colors
        
        self.generate_sprites()
        
        cols = int(self.columns_spin.get())
        rows = int(self.rows_spin.get())
        
        # individual sprite size
        w = int(self.pg_original_image.get_width()*self.scalex_var.get())
        h = int(self.pg_original_image.get_height()*self.scaley_var.get())
        sw = w/cols
        sh = h/rows
                
        # drawing sprite bounding lines
        for r in range(0,rows):
            
            pygame.draw.line(self.pg_sprites_image,CL.RED,(0,r*sh),(w,r*sh))
            pygame.draw.line(self.pg_sprites_image,CL.RED,(0,(r+1)*sh-1),(w,(r+1)*sh-1))
            for c in range(1,cols+1):                
        
                pygame.draw.line(self.pg_sprites_image,CL.RED,(c*sw-1,r*sh),(c*sw-1,(r+1)*sh))                
            #endfor
        #endfor
        
        self.update_canvas(self.pg_sprites_image)
        
    def update_indicator_widgets(self):
        
        w = self.pg_original_image.get_width()
        h = self.pg_original_image.get_height()
        
        size_str = '%ix%i'%(int(w),int(h))
        
        self.size_info_label.configure(text = size_str)
        
    def open_image(self):
        
        CL = GUIProperties.PG_Colors
        
        self.pg_original_image = pygame.image.load(self.file_path).convert()
        self.pg_original_image.set_colorkey(CL.BLACK)
        w= self.pg_original_image.get_width()
        h = self.pg_original_image.get_height()
        self.size = (w,h)

        return self.pg_original_image
    
    def scale_image(self,surf,new_width,new_height):
        
        return pygame.transform.smoothscale(surf,(new_width,new_height))
        
    def update_canvas(self,surf):
         
        self.sprite_canvas.draw(surf)        
        
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
        
        # animation widget
        self.sprite_animation_widget = SpriteAnimationWidget(self)  
        self.sprite_animation_widget.configure(width = C.ANIMATION_CANVAS_WIDTH,height = C.ANIMATION_CANVAS_HEIGHT)      
    
        self.selection_widget.pack(fill = tk.BOTH)   
        self.sprites_frame.pack(fill = tk.BOTH)
        self.sprite_animation_widget.pack(fill = tk.BOTH)
        
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
            
            