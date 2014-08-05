
class PlayerActionKeys:
    
        # action keys
    WALK_ACTION = 1
    STAND_ACTION = 2
    JUMP_ASCEND_ACTION = 3
    JUMP_MIDAIR_ACTION = 4
    JUMP_LAND_ACTION = 5
    JUMP_ATTACK_ACTION = 6
    
class ActionRule:
    
    def __init__(self):
        
        self.action_key = 0
        self.supercedes_actions = [] # list of actions that can be superceded by action key
        self.follows_actions = [] # list of actions that can be followed by action key
        
    def supercedes(self,action_requested_key):
        """
            Returns True if current action key is allow to supercede 'action_key'. False otherwise
        """        
        return self.supercedes_actions.count(action_requested_key) > 0
    
    def follows(self,action_requested_key):
        """
            Returns True if current action key is allow to follow after 'action_key'. False otherwise
        """        
        return self.follows_actions.count(action_requested_key) > 0

class ActionRuleSet:
    """
        Holds a resolution matrix for resolving the outcome of an action request        
    """
    
    def __init__(self):
        
        self.action_rules_dict = {}
        
    def add_rule(self,action_rule):
        """
            Adds an ActionRule object to the set
        """        
        self.action_rules_dict[action_rule.action_key] = action_rule
        
    def resolve_supercede(self,action_requested_key,action_interrogated_key):
        """
            Returns True if action_requested_key is allowed to supercede action_interrogated_key.  
            False otherwise
        """
        if self.action_rules_dict.has_key(action_requested_key):
            rule = self.action_rules_dict[action_requested_key]
            return rule.supercedes(action_interrogated_key)
        else:
            return False
        
    def resolve_follows(self,action_requested_key,action_interrogated_key):
        """
            Returns True if action_requested_key is allowed to follow action_interrogated_key.  
            False otherwise
        """
        if self.action_rules_dict.has_key(action_requested_key):
            rule = self.action_rules_dict[action_requested_key]
            return rule.follows(action_interrogated_key)
        else:
            return False
        
