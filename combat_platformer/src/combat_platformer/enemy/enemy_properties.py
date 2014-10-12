import pygame

class EnemyProperties(object):
    
    # size
    COLLISION_WIDTH = 88
    COLLISION_HEIGHT = 112
    
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
    MIN_DISTANCE_FROM_EDGE = 0.10 # percentage of width
    
    HANG_RADIUS = 5 # radius of circle use to check if an edge is near for hanging during fall
    HANG_DISTANCE_FROM_TOP = 12 # Used to set the distance from the top of the hanging platform to the top of the collision sprite
    HANG_DISTANCE_FROM_SIDE = 0
    
    CLIMB_DISTANCE_FROM_TOP = -5
    CLIMB_DISTANCE_FROM_SIDE = 0
    
    PATROL_AREA_RECTANGLE = pygame.Rect(0,0,500,100)
    SIGHT_AREA_RECTANGLE = pygame.Rect(0,0,200,100) 
    
    def __init__(self):
        
        self.collision_width = EnemyProperties.COLLISION_WIDTH
        self.collision_height = EnemyProperties.COLLISION_HEIGHT
        self.jump_speed = EnemyProperties.JUMP_SPEED
        self.super_jump_speed = EnemyProperties.SUPER_JUMP_SPEED
        self.run_speed = EnemyProperties.RUN_SPEED
        self.walk_speed = EnemyProperties.WALK_SPEED
        self.dash_speed = EnemyProperties.DASH_SPEED
        self.max_step_x = EnemyProperties.MAX_STEP_X
        self.max_midair_dashes = EnemyProperties.MAX_MIDAIR_DASHES
        self.inertial_reduction = EnemyProperties.INERTIA_REDUCTION
        
        self.max_distance_from_edge = EnemyProperties.MAX_DISTANCE_FROM_EDGE
        self.min_distance_from_edge = EnemyProperties.MIN_DISTANCE_FROM_EDGE
        
        self.hang_radius = EnemyProperties.HANG_RADIUS
        self.hang_distance_from_top = EnemyProperties.HANG_DISTANCE_FROM_TOP
        self.hang_distance_from_side = EnemyProperties.HANG_DISTANCE_FROM_SIDE
        
        self.climb_distance_from_top = EnemyProperties.CLIMB_DISTANCE_FROM_TOP
        self.climb_distance_from_side = EnemyProperties.CLIMB_DISTANCE_FROM_SIDE
        
        self.patrol_area_rect = EnemyProperties.PATROL_AREA_RECTANGLE
        self.patrol_walk_time = 10000
        self.patrol_unwary_time = 5000
        self.sight_area_rect = EnemyProperties.SIGHT_AREA_RECTANGLE
        
        self.alert_time = 5
        