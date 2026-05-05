import pygame

def load_arrow_images():
    arrow_images = {
        "up": [],
        "down": [],
        "left": [],
        "right": []
    }

    for i in range(0, 30):
        arrow_images["up"].append(
            pygame.transform.scale(
                pygame.image.load(f"Arrows/a{i}_up.png").convert_alpha(), (70, 70)
            )
        )
        arrow_images["down"].append(
            pygame.transform.scale(
                pygame.image.load(f"Arrows/a{i}_down.png").convert_alpha(), (70, 70)
            )
        )
        arrow_images["left"].append(
            pygame.transform.scale(
                pygame.image.load(f"Arrows/a{i}_left.png").convert_alpha(), (70, 70)
            )
        )
        arrow_images["right"].append(
            pygame.transform.scale(
                pygame.image.load(f"Arrows/a{i}_right.png").convert_alpha(), (70, 70)
            )
        )

    return arrow_images


class Arrow:
    def __init__(self, x, y, direction, arrow_images):
        self.direction = direction
        self.images = arrow_images[direction]
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.speed = 6
        self.animation_speed = 0.3

        self.spawn_time = pygame.time.get_ticks()

        if direction == "up":
            self.dx = 0
            self.dy = -self.speed
            self.rect = self.image.get_rect(center=(x, y))
            self.hitbox = pygame.Rect(0, 0, 16, 34)

        elif direction == "down":
            self.dx = 0
            self.dy = self.speed
            self.rect = self.image.get_rect(center=(x, y))
            self.hitbox = pygame.Rect(0, 0, 16, 34)

        elif direction == "left":
            self.dx = -self.speed
            self.dy = 0
            self.rect = self.image.get_rect(center=(x, y))
            self.hitbox = pygame.Rect(0, 0, 34, 16)

        elif direction == "right":
            self.dx = self.speed
            self.dy = 0
            self.rect = self.image.get_rect(center=(x, y))
            self.hitbox = pygame.Rect(0, 0, 34, 16)

        self.hitbox.center = self.rect.center

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.hitbox.center = self.rect.center

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.images):
            self.frame_index = 0

        self.image = self.images[int(self.frame_index)]

        if pygame.time.get_ticks() - self.spawn_time > 1250:
            return False

        return True

    def off_screen(self, width, height):
        return (
            self.rect.right < 0 or
            self.rect.left > width or
            self.rect.bottom < 0 or
            self.rect.top > height
        )

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 1)

    def hit_enemy(self, enemy_rect):

        return self.hitbox.colliderect(enemy_rect)