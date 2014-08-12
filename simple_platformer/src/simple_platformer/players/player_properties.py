class PlayerProperties(object):
    
    # Movement Defaults
    JUMP_SPEED = -10 # y axis points downwards
    SUPER_JUMP_SPEED = -12
    RUN_SPEED = 4
    DASH_SPEED = 8    
    MAX_X_POSITION_CHANGE = 8       
    INERTIA_REDUCTION = 0.14    
    MAX_MIDAIR_DASHES = 1
    
    # Environment thresholds
    MAX_DISTANCE_FROM_EDGE = 0.80 # percentage of width
    MIN_DISTANCE_FROM_EDGE = 0.40 # percentage of width
    
    def __init__(self):
        
        self.jump_speed = PlayerProperties.JUMP_SPEED
        self.super_jump_speed = PlayerProperties.SUPER_JUMP_SPEED
        self.run_speed = PlayerProperties.RUN_SPEED
        self.dash_speed = PlayerProperties.DASH_SPEED
        self.max_x_position_change = PlayerProperties.MAX_X_POSITION_CHANGE
        self.max_midair_dashes = PlayerProperties.MAX_MIDAIR_DASHES
        self.inertial_reduction = PlayerProperties.INERTIA_REDUCTION
        self.max_distance_from_edge = PlayerProperties.MAX_DISTANCE_FROM_EDGE
        self.min_distance_from_edge = PlayerProperties.MIN_DISTANCE_FROM_EDGE