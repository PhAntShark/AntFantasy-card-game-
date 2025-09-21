import pygame


class Matrix:
    def __init__(self, screen, rows=4, cols=5,
                 left_ratio=0.06, right_ratio=0.06, bottom_ratio=0.18, top_ratio=0.18):
        self.screen = screen
        self.rows = rows
        self.cols = cols
        self.left_ratio = left_ratio
        self.right_ratio = right_ratio
        self.bottom_ratio = bottom_ratio
        self.top_ratio = top_ratio
        self.update_dimensions()

    def update_dimensions(self):
        self.screen_width, self.screen_height = self.screen.get_size()

        # Calculate margins
        self.left_margin = int(self.screen_width * self.left_ratio)
        self.right_margin = int(self.screen_width * self.right_ratio)
        self.bottom_margin = int(self.screen_height * self.bottom_ratio)
        self.top_margin = int(self.screen_height * self.top_ratio)

        # Available play area
        self.avail_width = self.screen_width - \
            (self.left_margin + self.right_margin)
        self.avail_height = self.screen_height - \
            (self.top_margin + self.bottom_margin)

        # Calculate slot sizes independently for better space utilization
        self.slot_width = self.avail_width // self.cols
        self.slot_height = self.avail_height // self.rows

        # Actual board size using calculated slot dimensions
        self.width = self.cols * self.slot_width
        self.height = self.rows * self.slot_height

        # Center the board in the available space
        self.origin_x = self.left_margin + (self.avail_width - self.width) // 2
        self.origin_y = self.top_margin + \
            (self.avail_height - self.height) // 2

    def draw(self):
        self.update_dimensions()

        # Draw grid with rectangular slots
        for c in range(self.cols + 1):
            x = self.origin_x + c * self.slot_width
            pygame.draw.line(self.screen, (255, 255, 255),
                             (x, self.origin_y),
                             (x, self.origin_y + self.height), 2)

        for r in range(self.rows + 1):
            y = self.origin_y + r * self.slot_height
            pygame.draw.line(self.screen, (255, 255, 255),
                             (self.origin_x, y),
                             (self.origin_x + self.width, y), 2)

        # Opponent deck area (top left)
        opp_deck_width = self.left_margin - 20
        opp_deck_height = self.top_margin - 20
        opp_deck_rect = pygame.Rect(10, 10, opp_deck_width, opp_deck_height)
        pygame.draw.rect(self.screen, (255, 100, 100),
                         opp_deck_rect, 2)  # Red tint for opponent

        # Opponent graveyard (top right)
        opp_grave_width = self.right_margin - 20
        opp_gx = self.screen_width - self.right_margin + 10
        opp_grave_rect = pygame.Rect(
            opp_gx, 10, opp_grave_width, opp_deck_height)
        pygame.draw.rect(self.screen, (255, 100, 100),
                         opp_grave_rect, 2)  # Red tint for opponent

        # My deck area (bottom left)
        my_deck_width = self.left_margin - 20
        my_deck_height = self.bottom_margin - 20
        my_deck_y = self.screen_height - self.bottom_margin + 10
        my_deck_rect = pygame.Rect(
            10, my_deck_y, my_deck_width, my_deck_height)
        pygame.draw.rect(self.screen, (100, 100, 255),
                         my_deck_rect, 2)  # Blue tint for player

        # My graveyard (bottom right)
        my_grave_width = self.right_margin - 20
        my_gx = self.screen_width - self.right_margin + 10
        my_grave_rect = pygame.Rect(
            my_gx, my_deck_y, my_grave_width, my_deck_height)
        pygame.draw.rect(self.screen, (100, 100, 255),
                         my_grave_rect, 2)  # Blue tint for player

        # Opponent hand area (top center)
        opp_hand_rect = pygame.Rect(
            self.origin_x, 10, self.width, self.top_margin - 20)
        pygame.draw.rect(self.screen, (255, 100, 100),
                         opp_hand_rect, 2)  # Red tint for opponent

        # My hand area (bottom center)
        my_hand_rect = pygame.Rect(
            self.origin_x, my_deck_y, self.width, my_deck_height)
        pygame.draw.rect(self.screen, (100, 100, 255),
                         my_hand_rect, 2)  # Blue tint for player

    def get_slot_at_pos(self, pos):
        """Get the row, col of the slot at the given position"""
        x, y = pos
        if (self.origin_x <= x < self.origin_x + self.width
                and self.origin_y <= y < self.origin_y + self.height):
            col = (x - self.origin_x) // self.slot_width
            row = (y - self.origin_y) // self.slot_height
            return row, col
        return None

    def get_slot_rect(self, row, col):
        """Get the pygame.Rect for a specific slot"""
        x = self.origin_x + col * self.slot_width
        y = self.origin_y + row * self.slot_height
        return pygame.Rect(x, y, self.slot_width, self.slot_height)

    def get_area_at_pos(self, pos):
        """Determine which area was clicked (field, deck, graveyard, hand, etc.)"""
        x, y = pos

        # Check field grid first
        field_slot = self.get_slot_at_pos(pos)
        if field_slot:
            return {"type": "field", "row": field_slot[0], "col": field_slot[1]}

        # Check other areas
        areas = self.get_all_areas()

        for area_name, rect in areas.items():
            if rect.collidepoint(pos):
                return {"type": area_name}

        return None

    def get_all_areas(self):
        """Get all area rectangles for easy reference"""
        # Calculate positions
        opp_deck_height = self.top_margin - 20
        my_deck_height = self.bottom_margin - 20
        my_deck_y = self.screen_height - self.bottom_margin + 10
        opp_gx = self.screen_width - self.right_margin + 10
        my_gx = self.screen_width - self.right_margin + 10

        return {
            "opponent_deck": pygame.Rect(10, 10, self.left_margin - 20, opp_deck_height),
            "opponent_graveyard": pygame.Rect(opp_gx, 10, self.right_margin - 20, opp_deck_height),
            "opponent_hand": pygame.Rect(self.origin_x, 10, self.width, self.top_margin - 20),
            "my_deck": pygame.Rect(10, my_deck_y, self.left_margin - 20, my_deck_height),
            "my_graveyard": pygame.Rect(my_gx, my_deck_y, self.right_margin - 20, my_deck_height),
            "my_hand": pygame.Rect(self.origin_x, my_deck_y, self.width, my_deck_height)
        }
