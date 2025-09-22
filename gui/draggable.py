import pygame


class Draggable:
    def __init__(self, dst: pygame.Rect, is_draggable:bool = True):
        self.dst = dst
        self.is_dragging = False
        self.is_dropped = False
        self.is_draggable = is_draggable
        self.dx = 0
        self.dy = 0

    def handle_event(self, event):
        if self.is_draggable == True:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.dst.collidepoint(event.pos):
                    self.is_dragging = True
                    self.is_dropped = False
                    self.dx = self.dst.x - event.pos[0]
                    self.dy = self.dst.y - event.pos[1]

            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    self.dst.x = event.pos[0] + self.dx
                    self.dst.y = event.pos[1] + self.dy

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False
                    self.is_dropped = True
                
