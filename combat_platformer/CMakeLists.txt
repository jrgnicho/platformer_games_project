cmake_minimum_required(VERSION 2.8.3)
project(combat_platformer)


find_package(catkin REQUIRED COMPONENTS
)

 catkin_python_setup()



###################################
## catkin specific configuration ##
###################################
catkin_package(
    CATKIN_DEPENDS rospy simple_platformer
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

