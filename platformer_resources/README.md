## Blender Level Creation
- Guidelines:
	- Triangulate Meshes in Edit Mode -> Faces -> Triangulate (Ctrl-T)
	- Add "Game Property" integer code for each object in the "Logic Editor" panel.  
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
        - Use an "Empty Frame" as the parent object for all the platform components (rigid body, ledges, wall, surface and ceiling ghost nodes)
    - Select All object prior to exporting to egg.
