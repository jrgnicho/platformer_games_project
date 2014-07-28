import pygame
import os
from pygame.sprite import Sprite
import simple_platformer.utilities
from simple_platformer.utilities import *

class SpriteSet():
    
    def __init__(self):
        
        self.sprites = [] # Sprites
        self.rate_change = 0
        
    def load(self,file_name,details,rate):
        """
            Loads sprites from an image file
            - file : path to the image file
            - details : array of tuples of type (columns, rows) one per sprite
            - rate : frame rate at which to move to the next sprite in the list
            
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
                image = pygame.Surface([w, h]).convert()
                image.blit(sheet,(0,0),(x,y,w,h))
                image.set_colorkey(Colors.BLACK)
                self.sprites.append(image) 
            #endfor
        #endfor
        
        print "Loaded %i %ix%i sprites from image sheet %s "%(len(self.sprites),w,h,file_name)
        
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
        key = 0
        collecting_next = False
        for i in range(1,len(lines)):
            
            entries = lines[i].split(' ')        
            #print "File entry "+ str(entries)    
            
                        
            if len(entries) == 5:
                
                if collecting_next:
                    set = self.sprite_sets[key]
                    collecting_next = False
                else:
                    key = int(entries[0])
                    self.sprite_sets[key] = SpriteSet()
                    set = self.sprite_sets[key]
                
                #key = int(entries[0])
                image_file = os.path.join(parent_dir, entries[1])
                columns = int(entries[2])
                rows = int(entries[3])
                frate = int(entries[4])
                
                if not set.load(image_file,(columns,rows),frate):
                    return False
            
            #endif              

                
            if len(entries) == 6 and entries[5].count('N')>0:   
                
                if not collecting_next:
                    
                    key = int(entries[0])
                    self.sprite_sets[key] = SpriteSet()
                    set = self.sprite_sets[key] 
                    collecting_next = True
                    
                else:                  
                    set = self.sprite_sets[key] 
                      
                image_file = os.path.join(parent_dir, entries[1])
                columns = int(entries[2])
                rows = int(entries[3])
                frate = int(entries[4])
                
                if not set.load(image_file,(columns,rows),frate):
                    return False                  
                
            #endif
            
        #endfor
        
        return True
        