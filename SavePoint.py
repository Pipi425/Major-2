import pygame

# Image
SAVE_POINT_IMAGE = "Graphics/SavePoint.png"

# Data
SAVE_POINTS = {
    "cave_save": {
        "scene": "first_scene",
        "x": 280,
        "y": 220,
        "spawn_x": 280,
        "spawn_y": 300
    },

    "village_save": {
        "scene": "second_scene",
        "x": 560,
        "y": 610,
        "spawn_x": 617,
        "spawn_y": 720
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
            screen.blit(text1, (self.rect.x, self.rect.y - 50))
            screen.blit(text2, (self.rect.x, self.rect.y - 25))