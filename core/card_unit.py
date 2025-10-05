class CardUnit:
    def __init__(self, name, description, ability=None, card_type="Monster",
                 attack_points=0, defense_points=0, level_star=1, monster_name=None,
                 owner=None, pos='attack'):
        self.name = name
        self.description = description
        self.ability = ability
        self.card_type = card_type
        self.atk = attack_points
        self.defe = defense_points
        self.level_star = level_star
        self.monster_name = monster_name if monster_name else name
        self.pos = pos  # 'attack' or 'defense'
        self.owner = owner  # Player object
        self.is_summoned = False
        self.is_alive = True

    def switch_position(self):
        self.pos = 'defense' if self.pos == 'attack' else 'attack'
        print(f"{self.name} switched to {self.pos} position.")

    def show_info(self):
        print(f"{self.monster_name} | {self.name} | ATK: {self.atk} DEF: {self.defe} "
              f"Star: {self.level_star} Pos: {self.pos} | Type: {self.card_type}")
        

    def spell_card(self, ability):
        pass
    
    
    def trap_card(self, ability):
        pass
    
    @staticmethod
    def create_all_cards():
        genres = {
    "Monster": {
        "Scholar": [
            CardUnit("Apprentice Sorcerer", "A new mage", attack_points=1000, defense_points=500, level_star=1),
            CardUnit("Scholar Binh", "A student", attack_points=500, defense_points= 1000, level_star=1),
            CardUnit("Mage", "The mage that can good at control his power", attack_points=2200, defense_points=1000, level_star=2),
            CardUnit("Philosopher", "A chill guy", attack_points=1000, defense_points=2200, level_star=2),
            CardUnit("Senior Mage", "The mage that old has experience in many batle", attack_points=3000, defense_points=2500, level_star=3),
            CardUnit("Grand Mage", "The legendary of the mage", attack_points=4500, defense_points=3500, level_star=4),
        ],

        "Conqueror": [
            CardUnit("Archer man", "A new mage", attack_points=1000, defense_points=500, level_star=1),
            CardUnit("Sword man", "A student", attack_points=500, defense_points= 1000, level_star=1),
            CardUnit("Calavry", "The mage that can good at control his power", attack_points=2200, defense_points=1000, level_star=2),
            CardUnit("Executioner", "A chill guy", attack_points=1000, defense_points=2200, level_star=2),
            CardUnit("General", "The mage that old has experience in many batle", attack_points=3000, defense_points=2500, level_star=3),
            CardUnit("King", "The legendary of the mage", attack_points=4500, defense_points=3500, level_star=4),
        ],

        "Forest Monster": [
            CardUnit("Goblin", "A new mage", attack_points=1000, defense_points=500, level_star=1),
            CardUnit("Orc", "A student", attack_points=500, defense_points= 1000, level_star=1),
            CardUnit("Troll", "The mage that can good at control his power", attack_points=2200, defense_points=1000, level_star=2),
            CardUnit("Cyclope", "A chill guy", attack_points=1000, defense_points=2200, level_star=2),
            CardUnit("Werewolf", "The mage that old has experience in many batle", attack_points=3000, defense_points=2500, level_star=3),
            CardUnit("Monster King", "The legendary of the mage", attack_points=4500, defense_points=3500, level_star=4),
        ],

        "Demon": [
            CardUnit("Skeleton", "A new mage", attack_points=1000, defense_points=500, level_star=1),
            CardUnit("Lesser demon", "A student", attack_points=500, defense_points= 1000, level_star=1),
            CardUnit("Litch", "The mage that can good at control his power", attack_points=2200, defense_points=1000, level_star=2),
            CardUnit("Demon", "A chill guy", attack_points=1000, defense_points=2200, level_star=2),
            CardUnit("Vampire", "The mage that old has experience in many batle", attack_points=3000, defense_points=2500, level_star=3),
            CardUnit("Dullahan", "The legendary of the mage", attack_points=4500, defense_points=3500, level_star=4),
        ],

        "Scholar": [
            CardUnit("Apprentice Sorcerer", "A new mage", attack_points=1000, defense_points=500, level_star=1),
            CardUnit("Scholar", "A student", attack_points=500, defense_points= 1000, level_star=1),
            CardUnit("Mage", "The mage that can good at control his power", attack_points=2200, defense_points=1000, level_star=2),
            CardUnit("Philosopher", "A chill guy", attack_points=1000, defense_points=2200, level_star=2),
            CardUnit("Senior Mage", "The mage that old has experience in many batle", attack_points=3000, defense_points=2500, level_star=3),
            CardUnit("Grand Mage", "The legendary of the mage", attack_points=4500, defense_points=3500, level_star=4),
        ],

        "Forest Guard": [
            CardUnit("Elf", "A new mage", attack_points=1000, defense_points=500, level_star=1),
            CardUnit("Drawf", "A student", attack_points=500, defense_points= 1000, level_star=1),
            CardUnit("Dark Elf", "The mage that can good at control his power", attack_points=2200, defense_points=1000, level_star=2),
            CardUnit("Warrior", "A chill guy", attack_points=1000, defense_points=2200, level_star=2),
            CardUnit("Giant tree man", "The mage that old has experience in many batle", attack_points=3000, defense_points=2500, level_star=3),
            CardUnit("Forest god", "The legendary of the mage", attack_points=4500, defense_points=3500, level_star=4),
        ],
    }
}
    
    
    
        return genres   