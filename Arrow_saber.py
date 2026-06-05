import pygame


def load_arrow_images():
    return {
        "up": [],
        "down": [],
        "left": [],
        "right": []
    }


class Arrow:
    def __init__(self, x, y, direction, arrow_images):
        self.active = False

    def update(self):
        return False

    def off_screen(self, width, height):
        return True

    def draw(self, screen):
        pass

    def hit_enemy(self, enemy_rect):
        return False