import pygame

class Player:
    def __init__(self):
        self.up = []
        self.left = []
        self.down = []
        self.right = []

        for i in range(1, 4):
            self.up.append(pygame.transform.scale(pygame.image.load(f"Characters/u{i}.png").convert_alpha(), (45, 45)))
            self.left.append(pygame.transform.scale(pygame.image.load(f"Characters/l{i}.png").convert_alpha(), (45, 45)))
            self.down.append(pygame.transform.scale(pygame.image.load(f"Characters/d{i}.png").convert_alpha(), (45, 45)))
            self.right.append(pygame.transform.scale(pygame.image.load(f"Characters/r{i}.png").convert_alpha(), (45, 45)))

        self.animations = {
            "up": self.up,
            "left": self.left,
            "down": self.down,
            "right": self.right
        }

        self.x = 350
        self.y = 250
        self.direction = "down"
        self.frame = 0
        self.count = 0
        self.speed = 2

    def get_image(self):
        return self.animations[self.direction][self.frame]

    def get_rect(self):
        return pygame.Rect(self.x + 10, self.y + 32, 25, 10)

    def check_move(self, dx, dy, walls):
        test_rect = self.get_rect()
        test_rect = test_rect.move(dx, dy)
        for wall in walls:
            if test_rect.colliderect(wall):
                return False
        return True

    def move(self, keys, walls):
        moving = False
        dx = 0
        dy = 0

        if keys[pygame.K_a]:
            dx = -self.speed
            self.direction = "left"
        if keys[pygame.K_d]:
            dx = self.speed
            self.direction = "right"
        if keys[pygame.K_w]:
            dy = -self.speed
            self.direction = "up"
        if keys[pygame.K_s]:
            dy = self.speed
            self.direction = "down"

        if dx != 0 or dy != 0:
            if self.check_move(dx, dy, walls):
                self.x += dx
                self.y += dy
                moving = True

        if moving:
            self.count += 1
            if self.count >= 10:
                self.count = 0
                self.frame += 1
                if self.frame >= 3:
                    self.frame = 0
        else:
            self.frame = 1

    def draw(self, screen):
        screen.blit(self.get_image(), (self.x, self.y))