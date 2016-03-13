
## Character Behaviour
- [x] Add a momentum field to the CharacterStatus class in order to store pass that property among states.
- [x] MotionController must be moved to character module
- [x] Implement remaining actions: Air jump, dash, air dash, hang, climb, grab ledge
- [x] **Apply linear velocity relative to ReferenceNode.**
- [x] **Do not lock global y movement through the  setLinearFactor method of the BulletRigidBody class.**
- [x] **Use the Sector's class plane constraint to enforced relative 2D movement.**
- [ ] Implement Roll action which can be achieved during landing.
- [ ] Implement ClimbWall action. This might required some rearchitecturing of the Platform class
- [ ] Do not trigger Land action after short jumps
- [x] **Fix odd bouncing behaviour when landing near walls.  The solution to this is likely to be placing ghost nodes with WALL bitmask on each side of the platforms to prevent triggering SURFACE_LANDING type collisions**

## Level
- [ ] **Implement Sector transition through the use of BulletGhostNodes associated with a sector.**
- [ ] **Create Skybox.**

## State Machine
- [ ] State Machine shall arrange states in a stack so that when a state exits, then the SM will return to the previous state in the stack if no transition has been defined for the State|action pair that caused the exit.

## Camera
- [ ] __Fix CameraController trailing behaviour.__

## Input
- [ ] Fix the KeyboardController

## Documentation
- [ ] Document the properties in the CNS Fighter Factory file

## FF3 Character Resource Management
- [ ] Use the x, y offsets associated with a collision rectangle in the Animation Action structure in order to place the rectangle relative to the characters origin.

## Test Game
- [x] __Removed all unnecessary Ledge objects from platforms as the trigger Character Actions unnecessarily.__
