class rule_engine():
    def __init__(resolve_battle, updrage, pos, valid_move, applied_effect):
        self.resolve_battle = resolve_battle
        self.updrage = updrage
        self.valid_move = pos 
        self.applied_effect = applied_effect
        
    def Resolve_battle(attacker, defender):
        if defender.position == 'ATK':
            print('binh gay')