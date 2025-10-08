import pygame


class CardPreview:
    def __init__(self, x, y, width, height, border_color=(0, 0, 0), border_width=2):
        image_path = "assets/card-preview.png"
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = pygame.Rect(x, y, width, height)
        self.border_color = border_color
        self.border_width = border_width
        self.card_gui = None  # Will hold a resized CardGUI

    def set_card(self, card_ui):
        """Create a fresh CardGUI scaled to the preview size"""
        from gui.cards_gui.card_gui import CardGUI  # import here to avoid circular imports
        self.card_gui = CardGUI(card_ui.logic_card, pos=self.rect.topleft, size=(
            self.rect.width, self.rect.height))
        self.card_gui.image = self.card_gui.annotated_image

    def draw(self, screen):
        if self.card_gui:
            self.card_gui.rect.center = self.rect.center
            self.card_gui.draw(screen)

        else:
            screen.blit(self.image, self.rect)
