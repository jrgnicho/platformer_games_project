from xml.etree import ElementTree as ET
from pygame import Rect
from pygame.sprite import Sprite
from game_assets.object_assets import ObjectAssets
from game_assets.object_assets import AttackAssets
from game_assets.object_assets import AssetSet

class AssetCollectionXml(object):
    
    def __init__(self):
        
        self.tree = None
        self.root = None
        self.file_name = ''
        
    def open(self,file_name):
        
        self.file_name = file_name
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        
    def save(self, asset_sets,file_name):
        
        root = ET.Element('asset_collection')
        
        for set in asset_sets:
            
            self.write_asset_set_element(root, set)            
        #endfor
        
        ET.dump(root)
        tree = ET.ElementTree(root)
        xmlstr = ET.tostring(root, encoding='utf8', method='html')
        tree.write(file_name,encoding='utf8', method='xml')
    
    def write_asset_set_element(self,parent_elmt,set):
        
        asset_set_elemt = ET.SubElement(parent_elmt, 'asset_set', {'name':set.name})  
        
        for k in set.object_assets_dict.keys():            
            
            object_assets = set.object_assets_dict[k]
            #print "key %s,value: %s"%(k,str(object_assets))
            self.write_player_object_asset(asset_set_elemt, object_assets, set.name)
        #endfor
        
        return asset_set_elemt
        
    def write_player_object_asset(self,parent_elmt, asset ,set_name):
        
        object_elmt = ET.SubElement(parent_elmt, 'player_object', {'key':asset.key,'set':set_name})
        
        
        # animation asset
        animation_elmt = self.write_animation_asset(object_elmt, asset.animation)
        
        # right and left sprite sets
        self.write_sprite_list(animation_elmt, direction = 'RIGHT')
        self.write_sprite_list(animation_elmt, direction = 'LEFT',flipx = True)
        
        # collision group
        self.write_collision(object_elmt, asset.collision)
        
        
    def write_animation_asset(self,parent_elmt,animation_asset):
        
        animation_elmt = ET.SubElement(parent_elmt,'animation',{'frame_rate':str(animation_asset.frame_rate),
                                                               'layer':str(animation_asset.layer_drawing_priority)
                                                               })
        
        return animation_elmt
        
    def write_sprite_list(self,parent_elmt,file = 'image.png',cols = 1,rows = 1,scale = 1,
                              direction = 'RIGHT',flipx = False,flipy = False):
        
        sprite_list_elmt = ET.SubElement(parent_elmt,'sprite_list',{'image_file':file,
                                                       'cols':str(cols),
                                                       'rows':str(rows),
                                                       'scale':str(scale),
                                                       'direction':direction,
                                                       'flipx':str(flipx),
                                                       'flipy':str(flipy)
                                                       })
        
        return sprite_list_elmt

    def write_collision(self,parent_elmt,coll_group):
        
        collision_elmt = ET.SubElement(parent_elmt,'collision',{'collision_type_mask':str(coll_group.collision_type_mask),
                                                               'collision_with_mask':str(coll_group.collision_with_mask)
                                                               })
        
        for rect in iter(coll_group.rectangles):
            self.write_rect(collision_elmt, rect)
        
        return collision_elmt
        
        
    def write_rect(self,parent_elmt,rect):
        
        rect_elmt = ET.SubElement(parent_elmt, 'rect', {'x':str(rect.x),
                                                        'y':str(rect.y),
                                                         'width':str(rect.width),
                                                         'height':str(rect.height)})
        
        return rect_elmt