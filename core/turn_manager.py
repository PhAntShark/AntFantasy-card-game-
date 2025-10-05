from player import Player

class TurnManager:
    def __init__(self, players:list [Player]):
        self.players = players
        self.current_player_index = 0
        self.turn_count = 1   

    def current_player(self):
        return self.players[self.current_player_index]
    
    def opponent_player(self):
        other_index = (self.current_player_index +1 ) % len(self.players)
        return self.players[other_index]
    
    def start_turn(self):
        print(f'Turn {self.turn_count}  Start: Player{self.current_player().player_index}')
        
    def end_turn(self):
        print(f" Player {self.current_player().player_index} Turn Ends ")
        self.next_turn()
        
    def next_turn(self):
        self.current_player_index = (self.current_player_index +1 ) % len(self.players)
        if self.current_player_index == 0:
            self.turn_count +=1  
            print(f'turn {self.turn_count}')
