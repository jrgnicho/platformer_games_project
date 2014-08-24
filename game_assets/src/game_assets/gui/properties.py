
class GUIProperties(object):
    
    class Constants(object):
        
        WINDOW_WIDTH = 800
        WINDOW_HEIGHT = 600
        
        
    class Fonts(object):
        
        MAIN_TABS = ('Helvetica',14,'normal')#tkFont.Font(None,family= 'Helvetica',size= 14,weight = 'normal')
        COLLECTION_LABELS= ('Times',14,'bold')
        COLLECTION_INFO = ('Helvetica',14,'normal')
        SET_LABEL_FRAME = ('Helvetica',12,'normal')
        SET_SELECTION_LABEL = ('Helvetica',14,'normal')
        SET_COMBO_BOX = ('Symbol',14,'normal')
        
    
    class Names(object):
        
        TITLE = 'Asset Creator Tool'
        
        MAIN_NB_START_FRAME = 'Start'
        MAIN_NB_COLLECTION_FRAME= "Collection"
        COLLECTION_FRAME_LABEL = "Collection Name"
        COLLECTION_NB_SET_FRAME = 'Set'
        COLLECTION_NB_PLAYER_ACTION_FRAME = 'Player Actions'
        COLLECTION_NB_ATTACK_ACTION_FRAME = 'Attack Actions'  