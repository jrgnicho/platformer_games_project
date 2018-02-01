Platformer Game 
===============

Project that uses python libraries for creating a platformer style video game.


### Info
- This game library can be used with python 2.7 and 3.0 and has been built with the following libraries:
 
  - ROS:
    - See the [ros wiki](http://wiki.ros.org/indigo/Installation/Ubuntu) for installation instructions. Only the ROS-Base option is needed
    - This game only uses the **rospkg** module to locate directories and resources
    - The ROS command tools (roscd, rospack, rosrun, etc) can be used too

  - [tinyblend](https://github.com/gabdube/tinyblend)
    Used to read blender files into the game

  - Panda3D:
    - Game engine [Panda3D SDK](http://www.panda3d.org) 

  - Pygame:
    - 2D game engine.  Only the joystick module from this library is used 
    - Download from [source](https://bitbucket.org/pygame/pygame/wiki/VersionControl) and follow instructions in the wiki page.  Alternatively, you can install the debian however there is an
      issue with the joystick module which floods the console window with debug messages.


### Install Dependencies
The following python3 libraries need to be installed using the ```sudo pip3 install [pkg-name]``` command:

- panda3d
- rospkg
- shapely
- construct
- docutils



### Play
- Recomendations:
  A PS2 Joystick is recommended however the game will default to the keyboard if no joystick is plugged in.

- Run
  ```
  rosrun physics_platformer test_basic_game.py
  ```

  - You can run, jump, dash, double jump and hang from ledges.
  - Have fun ...
