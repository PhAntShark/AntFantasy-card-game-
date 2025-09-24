import pygame
from gui.hand import Hand


class GameAreaConfig:
    """Configuration constants for the game layout"""
    # Layout ratios
    LEFT_RATIO = 0.06
    RIGHT_RATIO = 0.06
    BOTTOM_RATIO = 0.18
    TOP_RATIO = 0.18

    # Spacing constants
    AREA_PADDING = 10
    AREA_BORDER_WIDTH = 2
    GRID_LINE_WIDTH = 2

    # Colors
    GRID_COLOR = (255, 255, 255)
    PLAYER_COLOR = (100, 100, 255)
    OPPONENT_COLOR = (255, 100, 100)


class GameArea:
    """Represents a rectangular game area with position and dimensions"""

    def __init__(self, x, y, width, height, color=None, border_width=2):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.border_width = border_width

    def draw(self, screen):
        if self.color:
            pygame.draw.rect(screen, self.color, self.rect, self.border_width)

    def contains_point(self, pos):
        return self.rect.collidepoint(pos)


class Matrix:
    def __init__(self, screen, players, rows=4, cols=5):
        self.screen = screen
        self.rows = rows
        self.cols = cols
        self.players = players
        self.config = GameAreaConfig()

        # Initialize areas (will be updated in update_dimensions)
        self.areas = {}
        self.hands = {}

        self.update_dimensions()
        self._create_hands()

    def update_dimensions(self):
        """Calculate all dimensions and create game areas"""
        screen_width, screen_height = self.screen.get_size()

        # Calculate margins
        margins = self._calculate_margins(screen_width, screen_height)

        # Calculate grid dimensions
        grid_info = self._calculate_grid_dimensions(
            screen_width, screen_height, margins)

        # Store grid information
        self.grid = grid_info

        # Create all game areas
        self._create_game_areas(screen_width, screen_height, margins)

    def _calculate_margins(self, screen_width, screen_height):
        """Calculate margin sizes based on screen dimensions"""
        return {
            'left': int(screen_width * self.config.LEFT_RATIO),
            'right': int(screen_width * self.config.RIGHT_RATIO),
            'top': int(screen_height * self.config.TOP_RATIO),
            'bottom': int(screen_height * self.config.BOTTOM_RATIO)
        }

    def _calculate_grid_dimensions(self, screen_width, screen_height, margins):
        """Calculate grid layout information"""
        # Available space for the grid
        avail_width = screen_width - (margins['left'] + margins['right'])
        avail_height = screen_height - (margins['top'] + margins['bottom'])

        # Slot dimensions
        slot_width = avail_width // self.cols
        slot_height = avail_height // self.rows

        # Actual grid size
        grid_width = self.cols * slot_width
        grid_height = self.rows * slot_height

        # Center the grid
        origin_x = margins['left'] + (avail_width - grid_width) // 2
        origin_y = margins['top'] + (avail_height - grid_height) // 2

        return {
            'origin_x': origin_x,
            'origin_y': origin_y,
            'width': grid_width,
            'height': grid_height,
            'slot_width': slot_width,
            'slot_height': slot_height
        }

    def _calculate_area_dimensions(self, margins):
        """Calculate dimensions for deck/graveyard areas"""
        deck_width = margins['left'] - (2 * self.config.AREA_PADDING)
        grave_width = margins['right'] - (2 * self.config.AREA_PADDING)

        return {
            'deck_width': max(0, deck_width),
            'grave_width': max(0, grave_width),
            'top_height': margins['top'] - (2 * self.config.AREA_PADDING),
            'bottom_height': margins['bottom'] - (2 * self.config.AREA_PADDING)
        }

    def _create_game_areas(self, screen_width, screen_height, margins):
        """Create all game areas (decks, graveyards, etc.)"""
        area_dims = self._calculate_area_dimensions(margins)
        padding = self.config.AREA_PADDING

        # Opponent areas (top)
        self.areas = {
            'opponent_deck': GameArea(
                padding, padding,
                area_dims['deck_width'], area_dims['top_height'],
                self.config.OPPONENT_COLOR, self.config.AREA_BORDER_WIDTH
            ),
            'opponent_graveyard': GameArea(
                screen_width - margins['right'] + padding, padding,
                area_dims['grave_width'], area_dims['top_height'],
                self.config.OPPONENT_COLOR, self.config.AREA_BORDER_WIDTH
            ),
            'opponent_hand_area': GameArea(
                self.grid['origin_x'], padding,
                self.grid['width'], margins['top'] - (2 * padding),
                None, 0  # Hand will draw itself
            ),

            # Player areas (bottom)
            'my_deck': GameArea(
                padding, screen_height - margins['bottom'] + padding,
                area_dims['deck_width'], area_dims['bottom_height'],
                self.config.PLAYER_COLOR, self.config.AREA_BORDER_WIDTH
            ),
            'my_graveyard': GameArea(
                screen_width - margins['right'] + padding,
                screen_height - margins['bottom'] + padding,
                area_dims['grave_width'], area_dims['bottom_height'],
                self.config.PLAYER_COLOR, self.config.AREA_BORDER_WIDTH
            ),
            'my_hand_area': GameArea(
                self.grid['origin_x'],
                screen_height - margins['bottom'] + padding,
                self.grid['width'], area_dims['bottom_height'],
                None, 0  # Hand will draw itself
            )
        }

    def _create_hands(self):
        """Create hand objects for players"""
        if len(self.players) >= 2:
            # Player hand (bottom)
            my_area = self.areas['my_hand_area']
            self.hands['my_hand'] = Hand(
                my_area.rect.x, my_area.rect.y,
                my_area.rect.width, my_area.rect.height,
                self.config.PLAYER_COLOR, self.config.AREA_BORDER_WIDTH,
                self.players[0]
            )

            # Opponent hand (top)
            opp_area = self.areas['opponent_hand_area']
            self.hands['opponent_hand'] = Hand(
                opp_area.rect.x, opp_area.rect.y,
                opp_area.rect.width, opp_area.rect.height,
                self.config.OPPONENT_COLOR, self.config.AREA_BORDER_WIDTH,
                self.players[1]
            )

    def draw(self):
        """Draw the entire game matrix"""
        self.update_dimensions()

        self._draw_grid()
        self._draw_areas()
        self._draw_hands()

    def _draw_grid(self):
        """Draw the playing field grid"""
        grid = self.grid

        # Vertical lines
        for col in range(self.cols + 1):
            x = grid['origin_x'] + col * grid['slot_width']
            pygame.draw.line(
                self.screen, self.config.GRID_COLOR,
                (x, grid['origin_y']),
                (x, grid['origin_y'] + grid['height']),
                self.config.GRID_LINE_WIDTH
            )

        # Horizontal lines
        for row in range(self.rows + 1):
            y = grid['origin_y'] + row * grid['slot_height']
            pygame.draw.line(
                self.screen, self.config.GRID_COLOR,
                (grid['origin_x'], y),
                (grid['origin_x'] + grid['width'], y),
                self.config.GRID_LINE_WIDTH
            )

    def _draw_areas(self):
        """Draw all game areas except hands"""
        for area_name, area in self.areas.items():
            if not area_name.endswith('_hand_area'):  # Skip hand areas
                area.draw(self.screen)

    def _draw_hands(self):
        """Draw player hands"""
        for hand in self.hands.values():
            hand.draw(self.screen)

    def get_slot_at_pos(self, pos):
        """Get the (row, col) of the grid slot at the given position"""
        x, y = pos
        grid = self.grid

        if (grid['origin_x'] <= x < grid['origin_x'] + grid['width'] and
                grid['origin_y'] <= y < grid['origin_y'] + grid['height']):

            col = (x - grid['origin_x']) // grid['slot_width']
            row = (y - grid['origin_y']) // grid['slot_height']
            return row, col

        return None

    def get_slot_rect(self, row, col):
        """Get the pygame.Rect for a specific grid slot"""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return None

        grid = self.grid
        x = grid['origin_x'] + col * grid['slot_width']
        y = grid['origin_y'] + row * grid['slot_height']

        return pygame.Rect(x, y, grid['slot_width'], grid['slot_height'])

    def get_area_at_pos(self, pos):
        """Determine which area was clicked"""
        # Check grid first
        slot = self.get_slot_at_pos(pos)
        if slot:
            return {"type": "field", "row": slot[0], "col": slot[1]}

        # Check other areas
        for area_name, area in self.areas.items():
            if area.contains_point(pos):
                # Remove '_area' suffix for hand areas
                clean_name = area_name.replace('_area', '')
                return {"type": clean_name}

        return None
    
    def get_graveyard_rect(self, player):
        """Return the pygame.Rect of the player's graveyard"""
        if player.is_opponent:
            return self.areas["opponent_graveyard"].rect
        else:
            return self.areas["my_graveyard"].rect