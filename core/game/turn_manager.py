class TurnManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.current_player_index = 0
        self.turn_count = 0

    def get_current_player(self):
        return self.game_state.players[self.current_player_index] 

    def get_next_player_index(self):
        return (self.current_player_index + 1) % len(self.game_state.players)

    def start_turn(self):
        print(f'Turn {self.turn_count}  Start: Player{
              self.get_current_player().player_index}')

    def end_turn(self):
        print(f" Player {self.get_current_player().player_index} Turn Ends ")
        self.game_state.player_info[self.get_current_player(
        )]["has_summoned"] = False
        self.game_state.player_info[self.get_current_player(
        )]["has_toggled"] = False
        self.current_player_index = self.get_next_player_index()
        self.turn_count += 1
        print(f'current turn {self.turn_count}')
        

    def get_phase_count(self):
        return self.turn_count // len(self.game_state.players)
