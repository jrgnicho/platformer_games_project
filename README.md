Platformer Game Project
===============

Project that uses python libraries for creating a platformer style video game.


### Install
- ROS:
  - See the [ros wiki](http://wiki.ros.org/indigo/Installation/Ubuntu) for installation instructions. Only the ROS-Base libraries are needed
  - Only the package indexing capabilities are used so this dependency shall go away in the future.

- Panda3D:
  - Download the corresponding [Panda3D SDK](http://www.panda3d.org/download.php?platform=ubuntu&version=1.9.1&sdk) and install using 'dpkg -i panda3d#####.deb' with the downloaded file

- Pygame:
  - Download from [source](https://bitbucket.org/pygame/pygame/wiki/VersionControl) and follow instructions in the wiki page.  Alternatively, you can install the debian however there is an
    issue with the joystick module where it prints lots of debug messages into the console when that module is used.

- Shapely:
  ```
  sudo pip install shapely
  ```

- Construct:
  ```
  sudo pip install construct
  ```


### Play
- Recomendations:
  A PS2 Joystick is recommended however you can still play with the keyboard if no joystick is plugged in.

- Run
  ```
  rosrun physics_platformer test_basic_game.py
  ```
