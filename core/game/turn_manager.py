from player import Player


class TurnManager:
    def __init__(self, players: list[Player]):
        self.players = players
        self.current_player_index = 0
        self.turn_count = 1

    def get_current_player(self):
        return self.players[self.current_player_index]

    def get_next_player_index(self):
        return (self.current_player_index + 1) % len(self.players)

    def start_turn(self):
        print(f'Turn {self.turn_count}  Start: Player{
              self.get_current_player().player_index}')

    def end_turn(self):
        print(f" Player {self.current_player().player_index} Turn Ends ")
        self.current_player_index = self.get_next_player_index()
        self.turn_count += 1

    def get_phase_count(self):
        return self.turn_count // len(self.players)
