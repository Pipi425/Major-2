import pygame


def load_melee_images():
    return {
        "down": [],
        "up": [],
        "left": [],
        "right": []
    }


class MeleeWeapon:
    def __init__(self, x, y, direction, melee_images):
        self.x = x
        self.y = y
        self.direction = direction

        self.life = 24
        self.hit_enemies = set()

        if direction == "right":
            self.attack_rect = pygame.Rect(x + 25, y - 22, 55, 44)

        elif direction == "left":
            self.attack_rect = pygame.Rect(x - 80, y - 22, 55, 44)

        elif direction == "up":
            self.attack_rect = pygame.Rect(x - 25, y - 70, 50, 50)

        else:
            self.attack_rect = pygame.Rect(x - 25, y + 25, 50, 50)

    def update(self):
        self.life -= 1

        if self.life <= 0:
            return False

        return True

    def hit_enemy(self, enemy):
        if enemy in self.hit_enemies:
            return False

        if self.attack_rect.colliderect(enemy.get_rect()):
            self.hit_enemies.add(enemy)
            return True

        return False

    def draw(self, screen):
        pass