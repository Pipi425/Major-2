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

        tempsurface = pygame.Surface((48, 22))
        tempimage = pygame.image.load(f"Arrows/a{i}_left.png").convert_alpha()
        tempsurface.blit(tempimage, (0, 0), (26, 39, 48, 22))
        arrow_images["left"].append(
            pygame.transform.scale(
                tempsurface.convert_alpha(), (70, 70)
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


        self.rect = self.image.get_rect(center = (x, y))

        self.speed = 6
        self.animation_speed = 0.3

        if direction == "up":
            self.dx = 0
            self.dy = -self.speed
        elif direction == "down":
            self.dx = 0
            self.dy = self.speed
        elif direction == "left":
            self.dx = -self.speed
            self.dy = 0
        elif direction == "right":
            self.dx = self.speed
            self.dy = 0

    def update(self, walls):
        self.rect.x += self.dx
        self.rect.y += self.dy

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.images):
            self.frame_index = 0

        self.image = self.images[int(self.frame_index)]

        for wall in walls:
            if self.rect.colliderect(wall):
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
        pygame.draw.rect(screen, (0, 255, 0), self.rect)
        screen.blit(self.image, self.rect)