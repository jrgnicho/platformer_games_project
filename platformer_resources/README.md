## Blender Level Creation
- Guidelines:
	- Download the YABEE export [plugin](https://github.com/09th/YABEE)
	- To export to egg select all objects that are to be exported (Press A in blender to Select All)
	- Triangulate Meshes in Edit Mode -> Faces -> Triangulate (Ctrl-T)
	- Add **object_type** "Game Property" as an integer code for each object in the "Logic Editor" panel.  Use the following codes:
      ```
        # high level elements
        START_LOCATION            = 6  # The player will first appear on the level at this location
        SECTOR                    = 7  # The 2D region that contains platforms and level objects. 
        SECTOR_TRANSITION         = 9
        SECTOR_ENTRY_LOCATION     = 10
        STATIC_PLATFORM           = 11

        # collision objects
        COLLISION_PLATFORM_RB     = 111
        COLLISION_LEDGE_RIGHT     = 112  # The ledge is to the right of the inmediate platform surface
        COLLISION_LEDGE_LEFT      = 114	 # The ledge is to the left of the inmediate platform surface
        COLLISION_SURFACE         = 115
        COLLISION_WALL            = 116  # The moving objects or players stand on it
        COLLISION_CEILING         = 117  # Usually the bottom of the platform

        # visual elements
        VISUAL_OBJECT             = 211
      ```
	- Make extensive use of parenting. All objects belonging to a sector need to be children of the node that represents the sector
	- Use the following axis convention:
		- X is forward
		- Z is up
		- Y points into the screen (Right-Hand rule)
	- Use the following naming convention:
		- Nested nodes names should be preceeded by the parent nodes names or a short version of it
		- Multiple nested names are separated by dots
		- For example a platform rigid body mesh that is part of platform 4 in sector 1 would be named as follows:  
				s1.p4.platform_rigid_body
        - For multiple objects of the same type at the same level in the node hierarchy use numeric suffixes to assign them a unique name.  For instance, if we had to platform rigid bodys their the names would be:
        	- s1.p4.platform_rigid_body1
        	- s1.p4.platform_rigid_body2
