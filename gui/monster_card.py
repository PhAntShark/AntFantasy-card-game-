from core.cards.monster_card import MonsterCard as LogicMonsterCard
from gui.sprite import Sprite
from typing import Tuple
from core.player import Player
from core.cards.monster_card import cardMode
from pathlib import Path
from pygame.draw import rect
from .draggable import Draggable
from pygame.transform import rotate
import pygame


class MonsterCard(LogicMonsterCard, Sprite, Draggable):
    def __init__(
        self,
        name: str,
        description: str,
        owner: Player,
        image_path: str | Path,
        pos: Tuple[float, float] = [0, 0],
        size: Tuple[float, float] = [0, 0],
        ability: str | None = None,
        attack_points: int = 0,
        defense_points: int = 0,
        level_star: int = 1,
        mode: cardMode = 'attack',
        rule_engine = None,
        **kwargs
    ):
        
        self.rule_engine = rule_engine
        # Initialize the logic part of the card
        LogicMonsterCard.__init__(
            self,
            name=name,
            description=description,
            owner=owner,
            ability=ability,
            attack_points=attack_points,
            defense_points=defense_points,
            level_star=level_star,
            mode=mode,
            **kwargs
        )
    

        # Initialize the visual part of the card
        Sprite.__init__(
            self,
            pos=pos,
            size=size,
            image_path=image_path,
            **kwargs
        )

        Draggable.__init__(self, self.rect)
        self.is_selected = False
        

    def update(self):
        if self.is_selected:
            rect(self.image, (255, 255, 0), self.rect, 3)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def toggle_mode(self):
        self.switch_position()
        if not self.rule_engine:
            print('djt me cuoc doi')
            return
        if self.rule_engine.can_toggle(self.owner):
            
            if self.mode == "defense":
                self.image = rotate(self.image, 90)
            else:
                self.image = rotate(self.image, -90)
            
            self.rule_engine.used_toggle(self.owner)
        else:
            print('no more turn for you fucking nigaga')


    # TODO: only allow toggle to be used once per turn
    # TODO: move handle toggle elsewhere
    def handle_toggle(self, event):
        if not self.rule_engine:
            print("Error: RuleEngine is not assigned to this card!")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            print(self.is_placed)
            if self.rect.collidepoint(event.pos) and self.is_placed and self.rule_engine.can_toggle(self.owner):
            #    if self.rule_engine.can_toggle(self.owner):
                   self.toggle_mode()
                   self.rule_engine.used_toggle(self.owner)
                # TODO: add player verification later
                
