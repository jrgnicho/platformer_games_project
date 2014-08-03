import pygame
import os
from pygame.sprite import Sprite
import simple_platformer.utilities
from simple_platformer.utilities import *

class SpriteSet():
    
    def __init__(self):
        
        self.sprites = [] # Sprites
        self.rate_change = 0
        
    def load(self,file_name,details,rate,sx = 1,sy = 1):
        """
            Loads sprites from an image file
            - file : path to the image file
            - details : array of tuples of type (columns, rows) one per sprite
            - rate : frame rate at which to move to the next sprite in the list.
            - sx : scale in the x direction
            - sy : scale in the y direction
            
            Return:
                - True : succeeded boolean
            
        """
        
        if not os.path.isfile(file_name):
            print "Image file %s not found"%(file_name)
            return False

        self.rate_change = rate;
        sheet = pygame.image.load(file_name).convert()
        
        columns = details[0]
        rows = details[1]
        srect = sheet.get_rect()
        
        # individual sprite size
        w = srect.width/columns
        h = srect.height/rows
        
        for j in range(0,rows):            
            for i in range(0,columns):                
                x = i * w
                y = j * h
                
                # extrating image
                image = pygame.Surface([w, h]).convert()
                image.blit(sheet,(0,0),(x,y,w,h))
                image.set_colorkey(Colors.BLACK)
                
                # scaling image                
                #scaled_width = int(sx*w)
                #scaled_height = int(sy*h)
                #scaled_image = pygame.Surface([scaled_width, scaled_height]).convert()
                #scaled_image = pygame.transform.smoothscale(image,(scaled_width,scaled_height))
                #scaled_image.set_colorkey(Colors.BLACK)
                self.sprites.append(image) 
                #self.sprites.append(scaled_image) 
            #endfor
        #endfor
        
        print "Loaded %i %ix%i sprites at scale %f x %f from image sheet %s "%(len(self.sprites),w,h,
                                                                               sx,sy,file_name)
        
        return True
        
    def len(self):
        
        return len(self.sprites)
    
    def get(self,index):
        
        return self.sprites[index]
    
    def invert_set(self):
        
        inv_set = SpriteSet();
        inv_set.rate_change = self.rate_change
        for sprite in self.sprites:
            
            inv_set.sprites.append(pygame.transform.flip(sprite,True,False))
            
        #endfor        
        return inv_set
    
   
    
    
class SpriteLoader():
    
    class Entry:
        
        def __init__(self):
            
            self.key = ''
            self.columns = 0
            self.image_file = ''
            self.rows = 0
            self.scale_x = 1
            self.frame_rate = 0
            self.scale_y = 1
            
        def parse_entry(self,line):
            
            entries = line.split(' ') 
            
            if len(entries) < 5 :
                return False  
                
            self.key = str(entries[0])      
            self.image_file = entries[1]
            self.columns = int(entries[2])
            self.rows = int(entries[3])
            self.frame_rate = int(entries[4]) # miliseconds
            
            if len(entries) >= 6:
                code = entries[5]
                self.scale_x = float(code[2:len(code)])
                
            if len(entries) >= 7:
                code = entries[6]
                self.scale_y = float(code[2:len(code)])
                
            return True
            
    
    def __init__(self):
        self.sprite_sets = {}
        
    def load_sets(self,desc_file_path):
        """
            Loads all of the sprites into a dictionary of sprite sets 
            and assign thems a unique key for indexing
            - desc_file_path: text file with the details of each sprite set to be loaded
                Each line shall be as follows:
                    key image_file columns rows framerate [N]
                    The last entry [N] is optional and it indicates that the
                    sprites in the next line are part of the same sprite set.
        """
                
        # getting parent directory of file
        parent_dir, file = os.path.split(desc_file_path)
        
        # check that file exists
        if not os.path.isfile(desc_file_path):
            return False         
        
        f = open(desc_file_path,'r')
        lines = f.readlines()
        
        set = SpriteSet()
        last_key = ''
        current_key = ''
        collecting_next = False
        entry = SpriteLoader.Entry()
        for i in range(1,len(lines)):
            
            if entry.parse_entry(lines[i]):
                
                current_key = entry.key
                if current_key != last_key: # create new set and storing                    
                    self.sprite_sets[current_key] = SpriteSet()
                    set = self.sprite_sets[current_key]
                    
                #endif
                
                entry.image_file = os.path.join(parent_dir, entry.image_file)
                
                if not set.load(entry.image_file,
                                (entry.columns,entry.rows),
                                entry.frame_rate,
                                entry.scale_x,
                                entry.scale_y):
                    
                    return False 
                #endif
                
            else:
                
                print "Failed to parse line %i"%(i)
                return False
            
            #endif
            
            last_key = current_key
            
        #endfor        
        return True
    
        