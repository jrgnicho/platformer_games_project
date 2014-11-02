from pygame import Rect

class PlayerProperties(object):
    
    # size
    COLLISION_WIDTH = 40
    COLLISION_HEIGH = 60
    
    # Movement Defaults
    JUMP_SPEED = -10 # y axis points downwards
    SUPER_JUMP_SPEED = -12
    WALK_SPEED = 2
    RUN_SPEED = 4
    DASH_SPEED = 8    
    MAX_STEP_X = 8       
    INERTIA_REDUCTION = 0.14    
    MAX_MIDAIR_DASHES = 1
    
    # Environment thresholds
    MAX_DISTANCE_FROM_EDGE = 0.80 # percentage of width
    MIN_DISTANCE_FROM_EDGE = 0.15 # percentage of width
    
    HANG_RADIUS = 5 # radius of circle use to check if an edge is near for hanging during fall
    HANG_DISTANCE_FROM_TOP = 12 # Used to set the distance from the top of the hanging platform to the top of the collision sprite
    HANG_DISTANCE_FROM_SIDE = 0
    
    CLIMB_DISTANCE_FROM_TOP = -5
    CLIMB_DISTANCE_FROM_SIDE = 0
    
    def __init__(self):
        
        self.collision_width = PlayerProperties.COLLISION_WIDTH
        self.collision_height = PlayerProperties.COLLISION_HEIGH
        self.jump_speed = PlayerProperties.JUMP_SPEED
        self.super_jump_speed = PlayerProperties.SUPER_JUMP_SPEED
        self.run_speed = PlayerProperties.RUN_SPEED
        self.walk_speed = PlayerProperties.WALK_SPEED
        self.dash_speed = PlayerProperties.DASH_SPEED
        self.max_step_x = PlayerProperties.MAX_STEP_X
        self.max_midair_dashes = PlayerProperties.MAX_MIDAIR_DASHES
        self.inertial_reduction = PlayerProperties.INERTIA_REDUCTION
        
        self.max_distance_from_edge = PlayerProperties.MAX_DISTANCE_FROM_EDGE
        self.min_distance_from_edge = PlayerProperties.MIN_DISTANCE_FROM_EDGE
        
        self.hang_radius = PlayerProperties.HANG_RADIUS
        self.hang_distance_from_top = PlayerProperties.HANG_DISTANCE_FROM_TOP
        self.hang_distance_from_side = PlayerProperties.HANG_DISTANCE_FROM_SIDE
        
        self.climb_distance_from_top = PlayerProperties.CLIMB_DISTANCE_FROM_TOP
        self.climb_distance_from_side = PlayerProperties.CLIMB_DISTANCE_FROM_SIDE