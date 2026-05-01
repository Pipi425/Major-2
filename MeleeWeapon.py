import pygame


def load_melee_images():
    melee_images = {
        "up": [],
        "down": [],
        "left": [],
        "right": []
    }

    for i in range(0, 5):
        melee_images["up"].append(
            pygame.transform.scale(
                pygame.image.load(f"MeleeWeapons/m{i}_up.png").convert_alpha(), (90, 90)
            )
        )
        melee_images["down"].append(
            pygame.transform.scale(
                pygame.image.load(f"MeleeWeapons/m{i}_down.png").convert_alpha(), (90, 90)
            )
        )
        melee_images["left"].append(
            pygame.transform.scale(
                pygame.image.load(f"MeleeWeapons/m{i}_left.png").convert_alpha(), (90, 90)
            )
        )
        melee_images["right"].append(
            pygame.transform.scale(
                pygame.image.load(f"MeleeWeapons/m{i}_right.png").convert_alpha(), (90, 90)
            )
        )

    return melee_images


class MeleeWeapon:
    def __init__(self, x, y, direction, melee_images):
        self.direction = direction
        self.images = melee_images[direction]
        self.frame_index = 0
        self.image = self.images[self.frame_index]

        self.animation_speed = 0.4

        offset = 45

        if direction == "up":
            self.rect = self.image.get_rect(center=(x, y - offset))
        elif direction == "down":
            self.rect = self.image.get_rect(center=(x, y + offset))
        elif direction == "left":
            self.rect = self.image.get_rect(center=(x - offset, y))
        elif direction == "right":
            self.rect = self.image.get_rect(center=(x + offset, y))

    def update(self):
        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.images):
            return False

        self.image = self.images[int(self.frame_index)]
        return True

    def hit_enemy(self, enemy_rect):
        return self.rect.colliderect(enemy_rect)

    def draw(self, screen):
        screen.blit(self.image, self.rect)