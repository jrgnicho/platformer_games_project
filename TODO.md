- [x] Modify GameObject constructor to optionally take a BulletNode type in its constructor instead of creating a BulletRigidBody by default
- [x] Make the current Platform class into a SimplePlatform which contains two ledges, two walls, a surface and a box rigid body.  Make a new Platform class that is a more generic one that can hold multiple ledges, walls, rigid bodies and that can be composed using the bullet rigid and ghost bodies.
- [ ] ~~Allow for the platform to have multiple rigid bodies located at an offset relative to the platforms coordinate system. It'd probably be best to setup the platforms main node as a empty BulletBodyNode and add all other bullet objects as children of the main node.~~ Use BulletRigidBody with multiple shapes instead.
- [ ] Create a class to load platforms, motion planes, and entire levels from a blender file that has been properly constructed
- [ ] Use the [addShapesFromCollisionSolids](https://www.panda3d.org/reference/1.9.4/python/panda3d.bullet.BulletBodyNode#a27ec9d5f2712032c5f6177860ed749a7) method to create bullet collision shapes from loaded models.
- [ ] Make game object rigid body into a capsule instead of a box to allow displacing along slanted surfaces.
- [ ] Rename the CharacterInfo class to CharacterProperties
- [x] Rename the CharacterStatus class to CharacterStateData