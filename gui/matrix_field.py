import pygame
from gui.game_area import GameArea, GameAreaConfig
from gui.hand import HandUI


class Matrix:
    def __init__(self, screen, game_state, rows=4, cols=5):
        self.screen = screen
        self.rows = rows
        self.cols = cols
        self.game_state = game_state
        self.config = GameAreaConfig()

        # Initialize areas (will be updated in update_dimensions)
        self.areas = {}

        self.update_dimensions()

        # TODO: refactor this area part
        self.hands = [self.areas["my_hand_area"],
                      self.areas["opponent_hand_area"]]

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
            'opponent_hand_area': HandUI(
                self.game_state.player_info[self.game_state.players[1]
                                            ]["held_cards"],
                self.grid['origin_x'], padding,
                self.grid['width'], margins['top'] - (2 * padding),
                self.config.OPPONENT_COLOR, self.config.AREA_BORDER_WIDTH
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
            'my_hand_area': HandUI(
                self.game_state.player_info[self.game_state.players[0]
                                            ]["held_cards"],
                self.grid['origin_x'],
                screen_height - margins['bottom'] + padding,
                self.grid['width'], area_dims['bottom_height'],
                self.config.PLAYER_COLOR, self.config.AREA_BORDER_WIDTH
            )
        }

    def draw(self):
        """Draw the entire game matrix"""
        self.update_dimensions()

        self._draw_grid()
        self._draw_areas()
        # self._draw_hands()

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
