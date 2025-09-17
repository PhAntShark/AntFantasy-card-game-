from monster_card import MonsterCard
from card import Card



field_matrix = [
['_']['_']['_']['_']['_'],
['_']['_']['_']['_']['_'],
['_']['_']['_']['_']['_'],
['_']['_']['_']['_']['_'],
['_']['_']['_']['_']['_'],
]

class CardUI(Card):
    def __init__(self, matrix,card: Card, row = '_', col = '_', **kwargs):
        super().__init__(**kwargs)
        self.card = card
        self.field_matrix = matrix
        self.row = row  
        self.col = col

@staticmethod
def placing_card(matrix, card: MonsterCard, row, col):
    if matrix[row][col] is '_':
        matrix[row][col] = card
        print(f'{card.name} placed at {row} row and {col} col ')
        
@staticmethod
def draw_matrix_ui(matrix):
    for row in matrix:
        print(row)
    
        

        

    
        
    
        

