import pygame


def load_arrow_images():
    down = pygame.image.load(
        "SkeletonSoldier/Arrow-NoOutline.png"
    ).convert_alpha()

    down = pygame.transform.scale(down, (18, 45))

    return {
        "down": down,
        "up": pygame.transform.rotate(down, 180),
        "right": pygame.transform.rotate(down, 90),
        "left": pygame.transform.rotate(down, -90)
    }


class Arrow:
    def __init__(self, x, y, direction, arrow_images):
        self.direction = direction
        self.image = arrow_images[direction]
        self.speed = 10
        self.spawn_time = pygame.time.get_ticks()

        # 保持玩家箭原来的位置，只向上2像素
        self.rect = self.image.get_rect(center=(x, y - 2))

        if direction == "up":
            self.dx = 0
            self.dy = -self.speed
            self.hitbox = pygame.Rect(0, 0, 10, 32)

        elif direction == "down":
            self.dx = 0
            self.dy = self.speed
            self.hitbox = pygame.Rect(0, 0, 10, 32)

        elif direction == "left":
            self.dx = -self.speed
            self.dy = 0
            self.hitbox = pygame.Rect(0, 0, 32, 10)

        else:
            self.dx = self.speed
            self.dy = 0
            self.hitbox = pygame.Rect(0, 0, 32, 10)

        self.hitbox.center = self.rect.center

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.hitbox.center = self.rect.center

        if pygame.time.get_ticks() - self.spawn_time > 1250:
            return False

        return True

    def off_screen(self, width, height):
        return (
            self.rect.right < 0
            or self.rect.left > width
            or self.rect.bottom < 0
            or self.rect.top > height
        )

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def hit_enemy(self, enemy_rect):
        return self.hitbox.colliderect(enemy_rect)