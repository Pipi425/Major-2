import pygame
import random

class Player:
    def __init__(self):
        self.up = []
        self.left = []
        self.down = []
        self.right = []
        self.walk_sound = []

        for i in range(1, 4):
            self.up.append(pygame.transform.scale(pygame.image.load(f"Characters/u{i}.png").convert_alpha(), (45, 45)))
            self.left.append(pygame.transform.scale(pygame.image.load(f"Characters/l{i}.png").convert_alpha(), (45, 45)))
            self.down.append(pygame.transform.scale(pygame.image.load(f"Characters/d{i}.png").convert_alpha(), (45, 45)))
            self.right.append(pygame.transform.scale(pygame.image.load(f"Characters/r{i}.png").convert_alpha(), (45, 45)))
            if i <= 3:
                self.walk_sound.append(pygame.mixer.Sound(f"SoundEffects/Stone{i}.mp3"))

        self.animations = {
            "up": self.up,
            "left": self.left,
            "down": self.down,
            "right": self.right
        }

        self.x = 297
        self.y = 389
        self.direction = "down"
        self.frame = 0
        self.count = 0
        self.speed = 2
        self.counter = 0

    def get_image(self):
        return self.animations[self.direction][self.frame]

    def get_rect(self):
        return pygame.Rect(self.x + 10, self.y + 32, 25, 15)

    def get_center(self):
        image = self.get_image()
        rect = image.get_rect(topleft=(self.x, self.y))
        return rect.center

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
            self.counter += 1
            if self.counter >= 20:
                random.choice(self.walk_sound).play()
                self.counter = 0
            if self.count >= 10:
                self.count = 0
                self.frame += 1
                if self.frame >= 3:
                    self.frame = 0
        else:
            self.frame = 1

    def draw(self, screen):
        screen.blit(self.get_image(), (self.x, self.y))