import pygame

# Image
SAVE_POINT_IMAGE = "Graphics/SavePoint.png"

# Data
SAVE_POINTS = {
    "cave_save": {
        "scene": "first_scene",
        "x": 275,
        "y": 220,
        "spawn_x": 297,
        "spawn_y": 389
    },

    "village_save": {
        "scene": "second_scene",
        "x": 595,
        "y": 32,
        "spawn_x": 617,
        "spawn_y": 720
    },

    "eldermoor_save": {
        "scene": "eldermoor_scene",
        "x": 595,
        "y": 352,
        "spawn_x": 617,
        "spawn_y": 720
    },

    "SnowVillage_save": {
        "scene": "SnowVillage",
        "x": 291,
        "y": 352,
        "spawn_x": 1248,
        "spawn_y": 288
    },
    "Maze_save": {
        "scene": "Maze",
        "x": 83,
        "y": 592,
        "spawn_x": 134,
        "spawn_y": 540
    },
    "IroHouse_save": {
        "scene": "IroHouse",
        "x": 483,
        "y": 400,
        "spawn_x": 617,
        "spawn_y": 720
    },
    "IroHome_save": {
        "scene": "IroHome",
        "x": 595,
        "y": 300,
        "spawn_x": 617,
        "spawn_y": 720
    },
    "MazeSolved_save": {
        "scene": "Maze_Solved",
        "x": 83,
        "y": 592,
        "spawn_x": 134,
        "spawn_y": 540
    },
    "DesertVillage_save": {
        "scene": "DesertVillage",
        "x": 100,
        "y": 290,
        "spawn_x": -40,
        "spawn_y": 362
    },
    "PreRoom_save": {
        "scene": "PreRoom",
        "x": 994,
        "y": 400,
        "spawn_x": 970,
        "spawn_y": 660
    }

}


class SavePoint:
    def __init__(self, save_point_id):
        # ID
        self.save_point_id = save_point_id

        # Data
        point = SAVE_POINTS[save_point_id]

        # Image
        self.image = pygame.image.load(SAVE_POINT_IMAGE).convert_alpha()
        self.image = pygame.transform.scale(self.image, (90, 90))

        # Rect
        self.rect = self.image.get_rect(topleft=(point["x"], point["y"]))

    def get_rect(self):
        # Wall
        return self.rect

    def is_near(self, player):
        # Range
        check_rect = self.rect.inflate(100, 100)

        # Check
        return check_rect.colliderect(player.get_rect())

    def draw(self, screen, near_player):
        # Draw
        screen.blit(self.image, self.rect)

        if near_player:
            # Font
            font = pygame.font.SysFont(None, 25)

            # Text
            text1 = font.render("P: Save", True, (255, 255, 255))
            text2 = font.render("R: Reset", True, (255, 255, 255))

            # Show
            screen.blit(text1, (self.rect.x, self.rect.y + 50))
            screen.blit(text2, (self.rect.x, self.rect.y + 75))