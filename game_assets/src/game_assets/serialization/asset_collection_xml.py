from xml.etree import ElementTree as ET

class AssetCollectionXml(object):
    
    def __init__(self):
        
        self.tree = None
        self.root = None
        self.file_name = ''
        
    def open(self,file_name):
        
        self.file_name = file_name
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        
    def save(self):
        pass
        
    def write(self,file_name):
        
        # writing player action asset
        player_action_elmt = ET.SubElement(self.tree, 'player_action', {('key','ACTION1'),('set','PlayerActions')})
        animation_elmt = ET.SubElement(player_action_elmt,'animation',{('image_file','my_sprite_sheet.png'),
                                                                       ('cols',str(2)),
                                                                       ('rows',str(1)),
                                                                       ('scale',str(1.5)),
                                                                       ('frame_rate',str(100)),
                                                                       ('layer',str(0))
                                                                       ('direction','RIGHT'),
                                                                       ('mirror',str(True))})
        
        collision_elmt = ET.SubElement(player_action_elmt,'collision',{('collision_type_mask',str(0)),
                                                                       ('collision_with_mask',str(1))})