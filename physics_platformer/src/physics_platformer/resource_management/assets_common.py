class ObjectTypeID(object):
  """
  The egg file should contains Tags with the 'object_type' custom property which is set
  to one of the values below.
  """
  
  
  # high level elements
  START_POSITION            = 6
  SECTOR                    = 7
  SECTOR_TRANSITION         = 9
  SECTOR_ENTRY_POINT        = 10
  STATIC_PLATFORM           = 11
  
  # collision objects
  COLLISION_PLATFORM_RB     = 111
  COLLISION_LEDGE_RIGHT     = 112
  COLLISION_LEDGE_LEFT      = 114
  COLLISION_SURFACE         = 115
  COLLISION_WALL            = 116
  COLLISION_CEILING         = 117
  
  # visual elements
  VISUAL_OBJECT             = 211
  
  
  
class CustomProperties(object):  
  """
  One or more of these custom properties should be included in the objects loaded from the resource file.
  These properties are retrieval with the NodePath.getTag() method.
  In blender, they can be added in the game logic section, see here for more info https://www.panda3d.org/forums/viewtopic.php?t=11441
  """
  
  OBJECT_TYPE_INT = 'object_type'