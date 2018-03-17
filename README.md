Platformer Game 
===============

Project that uses python libraries for creating a platformer style video game.


### Info
- This game code can be used with python 2.7 and 3.0 (recommended) and has been built with the following libraries:
 
  - ROS:
    - See the [ros wiki](http://wiki.ros.org/indigo/Installation/Ubuntu) for installation instructions. Only the ROS-Base option is needed
    - This game only uses the **rospkg** module to locate directories and resources
    - The ROS command tools (roscd, rospack, rosrun, etc) can be used too

  - Panda3D:
    - Game engine [Panda3D SDK](http://www.panda3d.org) 

  - Pygame:
    - 2D game engine.  Only the joystick module from this library is used 
    - The source code can be downloaded from [here](https://bitbucket.org/pygame/pygame/wiki/VersionControl).  However, it's preferable to install through pip3


### Install Dependencies
The following python3 libraries need to be installed using the ```sudo pip3 install [pkg-name]``` command:

- panda3d
- rospkg
- shapely
- construct
- docutils
- pygame
- ... and more.  Just install the libraries python complains about when you try to run the demos.



### Play
- Recomendations:
  A PS2 Joystick is recommended (USB adapted is needed) however the game will default to the keyboard if no joystick is plugged in.
- Joystick Controls (PS2)
  - Jump X
  - Dash R1
  - Move right or left D-PAD
  - Climb Up D-PAD (Hanging on ledge only)
- Keyboard Controls
  - Dash Q
  - Jump S
  - Move right or left Use Arrows
  - Climb Up Arrow Up (Hanging on ledge only)

- The demos are located in the `physics_plaformer/demos/` directory.
- Run demo 1:
  ```
  python3 demo_basic_game.py
  ```
  The level in this demo was procedurally generated

- Run demo 2:
  ```
  python3 demo_simple_level.py
  ```
  The level in this demo was created in blender.  More on level creation in blender [here](platformer_resources/README.md)
  This demo is pretty buggy at the moment.


- In both these demo you can run, jump, dash, double jump and hang from ledges.
- Have fun ...
