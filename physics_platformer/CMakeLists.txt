cmake_minimum_required(VERSION 2.8.3)
project(physics_platformer)

## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
)

catkin_python_setup()

###################################
## catkin specific configuration ##
###################################
catkin_package(
  CATKIN_DEPENDS python-bitarray panda3d python-pygame
)

###########
## Build ##
###########

include_directories(
  ${catkin_INCLUDE_DIRS}
)

#############
## Install ##
#############

#############
## Testing ##
#############
