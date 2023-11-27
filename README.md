Platformer Game 
===============

Project that uses python libraries for creating a platformer style video game.


### Info
- This game code can be used with python 2.7 and 3.0 (recommended) and has been built with the following libraries:
  - Panda3D:
    - Game engine [Panda3D SDK](http://www.panda3d.org) 

  - Pygame:
    - 2D game engine.  Only the joystick module from this library is used 
    - The source code can be downloaded from [here](https://bitbucket.org/pygame/pygame/wiki/VersionControl).  However, it's preferable to install through pip3


### Install Dependencies
- Use pip3 to install the game dependencies.  Locate the `requirements.txt` file and run the following command:
	```
		sudo pip3 install -r requirements.txt
	```

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

- The demos are located in the `platformer_core/demos/` directory.
- Run demo 1:
  ```
  python3 demos/demo_basic_game.py
  ```
  The level in this demo was procedurally generated

- Run demo 2:
  ```
  python3 demos/demo_simple_level.py
  ```
  The level in this demo was created in blender.  More on level creation in blender [here](platformer_resources/README.md)
  This demo is pretty buggy at the moment.


- In both these demo you can run, jump, dash, double jump and hang from ledges.
- Have fun ...
