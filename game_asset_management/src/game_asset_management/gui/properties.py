
class GUIProperties(object):
    
    IMAGE_FORMATS = [                     
        ('Portable Network Graphics','*.png'),
        ('Windows Bitmap','*.bmp'),
        ('JPEG / JFIF','*.jpg'),
        ('CompuServer GIF','*.gif'),
        ]
    
    class Constants(object):
        
        WINDOW_WIDTH = 1200
        WINDOW_HEIGHT = 1000
        SPRITE_SHEET_CANVAS_WIDTH = 600
        SPRITE_SHEET_CANVAS_HEIGHT = 150
        ANIMATION_CANVAS_WIDTH = 200
        ANIMATION_CANVAS_HEIGHT = 200
        
    class PG_Colors(object):
        BLACK    = (   0,   0,   0)
        WHITE    = ( 255, 255, 255)
        BLUE     = (   0,   0, 255)
        RED      = ( 255,   0,   0)
        GREEN    = (   0, 255,   0)
        LIGHT_BLUE = (0,255,255)
        
        
    class Fonts(object):
        
        MAIN_TABS = ('Helvetica',14,'normal')#tkFont.Font(None,family= 'Helvetica',size= 14,weight = 'normal')
        COLLECTION_LABELS= ('Times',14,'bold')
        COLLECTION_INFO = ('Helvetica',14,'normal')
        SET_LABEL_FRAME = ('Helvetica',12,'normal')
        SET_SELECTION_LABEL = ('Helvetica',14,'normal')
        SET_COMBO_BOX = ('Symbol',14,'normal')
        SET_BUTTON = ('Times',14,'normal')
        SPRITE_WIDGET_SPIN = ('Times',14,'normal')
        
    
    class Names(object):
        
        TITLE = 'Asset Creator Tool'
        
        MAIN_NB_START_FRAME = 'Start'
        MAIN_NB_COLLECTION_FRAME= "Collection"
        COLLECTION_FRAME_LABEL = "Collection Name"
        COLLECTION_NB_SET_FRAME = 'Set'
        ACTION_NB_ANIMATION_FRAME = 'Animation'
        ACTION_NB_COLLISION_FRAME = 'Collision'
        ACTION_NB_ATTACK_FRAME = 'Attack'  