import pygame
import random

class Player:
    def __init__(self):
        self.up = []
        self.up_hit = []
        self.left = []
        self.left_hit = []
        self.down = []
        self.down_hit = []
        self.right = []
        self.right_hit = []
        self.walk_sound = []
        self.hurt_sound = []

        self.hit = False
        self.hit_timer = 0
        self.hit_flash_counter = 0

        for i in range(1, 4):
            self.up.append(pygame.transform.scale(pygame.image.load(f"Characters/u{i}.png").convert_alpha(), (45, 45)))
            self.left.append(pygame.transform.scale(pygame.image.load(f"Characters/l{i}.png").convert_alpha(), (45, 45)))
            self.down.append(pygame.transform.scale(pygame.image.load(f"Characters/d{i}.png").convert_alpha(), (45, 45)))
            self.right.append(pygame.transform.scale(pygame.image.load(f"Characters/r{i}.png").convert_alpha(), (45, 45)))

            self.up_hit.append(pygame.transform.scale(pygame.image.load(f"Characters/u{i}_hit.png").convert_alpha(), (45, 45)))
            self.left_hit.append(pygame.transform.scale(pygame.image.load(f"Characters/l{i}_hit.png").convert_alpha(), (45, 45)))
            self.down_hit.append(pygame.transform.scale(pygame.image.load(f"Characters/d{i}_hit.png").convert_alpha(), (45, 45)))
            self.right_hit.append(pygame.transform.scale(pygame.image.load(f"Characters/r{i}_hit.png").convert_alpha(), (45, 45)))

            self.walk_sound.append(pygame.mixer.Sound(f"SoundEffects/Stone{i}.mp3"))

        for i in self.walk_sound:
            i.set_volume(0.5)

        for i in range(1, 8):
            self.hurt_sound.append(pygame.mixer.Sound(f"HurtSounds/Hurt{i}.mp3"))
            print(i)
            self.hurt_sound[i - 1].set_volume(0.5)

        self.animations = {
            "up": self.up,
            "left": self.left,
            "down": self.down,
            "right": self.right
        }

        self.hit_animations = {
            "up": self.up_hit,
            "left": self.left_hit,
            "down": self.down_hit,
            "right": self.right_hit
        }

        self.x = 297
        self.y = 389
        self.direction = "down"
        self.frame = 0
        self.count = 0
        self.speed = 2
        self.counter = 0

    def get_image(self):
        normal = self.animations[self.direction][self.frame]

        if not self.hit:
            return normal

        if (self.hit_flash_counter // 5) % 2 == 0:
            return normal
        else:
            return self.hit_animations[self.direction][self.frame]

    def get_rect(self):
        return pygame.Rect(self.x + 10, self.y + 32, 25, 15)

    def get_hurt_rect(self):
        return pygame.Rect(self.x, self.y, 45, 45)

    def get_center(self):
        image = self.get_image()
        rect = image.get_rect(topleft=(self.x, self.y))
        return rect.center

    def take_hit(self):
        if not self.hit:
            random.choice(self.hurt_sound).play()
            self.hit = True
            self.hit_timer = 30

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
            if self.check_move(dx, 0, walls):
                self.x += dx
                moving = True

            if self.check_move(0, dy, walls):
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

        if self.hit:
            self.hit_timer -= 1
            self.hit_flash_counter += 1

            if self.hit_timer <= 0:
                self.hit = False
                self.hit_flash_counter = 0

    def draw(self, screen):
        screen.blit(self.get_image(), (self.x, self.y))