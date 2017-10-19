cmake_minimum_required(VERSION 2.8.3)
project(panda3d_examples)

find_package(catkin REQUIRED COMPONENTS
)

###################################
## catkin specific configuration ##
###################################
catkin_package(
  CATKIN_DEPENDS panda3d python-pygame rospy
)

###########
## Build ##
###########

#############
## Install ##
#############

#############
## Testing ##
#############

