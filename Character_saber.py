import pygame
import random


SIZE = (140, 140)
DIRECTIONS = ["down", "up", "left", "right"]


def load_images(path, size):
    sheet = pygame.image.load(path).convert_alpha()

    images = []

    frame_count = 8
    frame_width = sheet.get_width() // frame_count
    frame_height = sheet.get_height()

    for i in range(frame_count):
        image = sheet.subsurface(
            pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        ).copy()

        image = pygame.transform.scale(image, size)
        images.append(image)

    return images


class Player:
    def __init__(self, spawn_x, spawn_y):
        self.walk_sound = []
        self.hurt_sound = []

        self.hit = False
        self.hit_timer = 0
        self.hit_flash_counter = 0

        self.idle = {}
        self.run = {}
        self.attack = {}

        for direction in DIRECTIONS:
            self.idle[direction] = load_images(
                "Characters/idle_" + direction + ".png",
                SIZE
            )

            self.run[direction] = load_images(
                "Characters/run_" + direction + ".png",
                SIZE
            )

            attack1 = load_images(
                "Characters/attack1_" + direction + ".png",
                SIZE
            )

            attack2 = load_images(
                "Characters/attack2_" + direction + ".png",
                SIZE
            )

            self.attack[direction] = [attack1, attack2]

        for i in range(1, 4):
            self.walk_sound.append(pygame.mixer.Sound(f"SoundEffects/Stone{i}.mp3"))

        for sound in self.walk_sound:
            sound.set_volume(0.5)

        for i in range(1, 8):
            self.hurt_sound.append(pygame.mixer.Sound(f"HurtSounds/Hurt{i}.mp3"))
            self.hurt_sound[i - 1].set_volume(0.5)

        self.x = spawn_x
        self.y = spawn_y

        self.direction = "down"

        self.frame = 0
        self.count = 0

        self.speed = 3
        self.fast_speed = 5

        self.counter = 0
        self.moving = False

        self.attacking = False
        self.attack_frame = 0
        self.attack_count = 0
        self.attack_images = self.attack["down"][0]
        self.attack_direction = "down"
        self.attack_key_down = False
        self.attack_cooldown = 0

        self.max_health = 1000
        self.health = 1000
        self.hp = self.health

        self.dead = False

        self.defense = 0
        self.weapon = None
        self.armor = None

        self.Full_heart = pygame.transform.scale(
            pygame.image.load("HealthBars/Full_heart.png").convert_alpha(), (40, 40)
        )
        self.Half_heart = pygame.transform.scale(
            pygame.image.load("HealthBars/Half_heart.png").convert_alpha(), (40, 40)
        )
        self.Empty_heart = pygame.transform.scale(
            pygame.image.load("HealthBars/Empty_heart.png").convert_alpha(), (40, 40)
        )

    def start_attack(self):
        if self.attacking:
            return

        if self.attack_cooldown > 0:
            return

        if self.weapon is None:
            return

        self.attacking = True
        self.moving = False

        self.attack_direction = self.direction
        self.attack_images = random.choice(self.attack[self.attack_direction])

        self.attack_frame = 0
        self.attack_count = 0

        self.attack_cooldown = 45

    def update_attack(self):
        if not self.attacking:
            return

        self.attack_count += 1

        if self.attack_count >= 3:
            self.attack_count = 0
            self.attack_frame += 1

            if self.attack_frame >= len(self.attack_images):
                self.attack_frame = 0
                self.attacking = False

    def update_hit_timer(self):
        if self.hit:
            self.hit_timer -= 1
            self.hit_flash_counter += 1

            if self.hit_timer <= 0:
                self.hit = False
                self.hit_flash_counter = 0

    def get_image(self):
        if self.attacking:
            image = self.attack_images[self.attack_frame]

        elif self.moving:
            images = self.run[self.direction]

            if self.frame >= len(images):
                self.frame = 0

            image = images[self.frame]

        else:
            images = self.idle[self.direction]

            if self.frame >= len(images):
                self.frame = 0

            image = images[self.frame]

        if not self.hit:
            return image

        if (self.hit_flash_counter // 5) % 2 == 0:
            return image

        flash_image = image.copy()
        flash_image.set_alpha(120)
        return flash_image

    def get_rect(self):
        return pygame.Rect(self.x + 52, self.y + 98, 36, 18)

    def get_hurt_rect(self):
        return pygame.Rect(self.x + 42, self.y + 42, 56, 88)

    def get_center(self):
        image = self.get_image()
        rect = image.get_rect(topleft=(self.x, self.y))
        return rect.center

    def take_hit(self):
        if not self.hit and not self.dead:
            random.choice(self.hurt_sound).play()

            self.hit = True
            self.hit_timer = 30
            self.hit_flash_counter = 0

            self.health -= 1
            self.hp = self.health

            if self.health <= 0:
                self.health = 0
                self.hp = 0
                self.dead = True

    def check_move(self, dx, dy, walls):
        test_rect = self.get_rect()
        test_rect = test_rect.move(dx, dy)

        for wall in walls:
            if test_rect.colliderect(wall):
                return False

        return True

    def move(self, keys, walls):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if keys[pygame.K_j]:
            if not self.attack_key_down:
                self.start_attack()
                self.attack_key_down = True
        else:
            self.attack_key_down = False

        if self.attacking:
            self.moving = False
            self.update_attack()
            self.update_hit_timer()
            return

        self.moving = False

        dx = 0
        dy = 0

        speed = self.speed

        if keys[pygame.K_LSHIFT]:
            speed = self.fast_speed

        if keys[pygame.K_a]:
            dx = -speed
            self.direction = "left"

        if keys[pygame.K_d]:
            dx = speed
            self.direction = "right"

        if keys[pygame.K_w]:
            dy = -speed
            self.direction = "up"

        if keys[pygame.K_s]:
            dy = speed
            self.direction = "down"

        if dx != 0 or dy != 0:
            if self.check_move(dx, 0, walls):
                self.x += dx
                self.moving = True

            if self.check_move(0, dy, walls):
                self.y += dy
                self.moving = True

        self.count += 1

        if self.moving:
            self.counter += 1

            if self.counter >= 18:
                random.choice(self.walk_sound).play()
                self.counter = 0

            if self.count >= 6:
                self.count = 0
                self.frame += 1

                if self.frame >= len(self.run[self.direction]):
                    self.frame = 0

        else:
            if self.count >= 12:
                self.count = 0
                self.frame += 1

                if self.frame >= len(self.idle[self.direction]):
                    self.frame = 0

        self.update_hit_timer()

    def draw(self, screen):
        screen.blit(self.get_image(), (self.x, self.y))

    def draw_health_bar(self, screen):
        heart_x = 20
        heart_y = 20
        spacing = 40

        for i in range(3):
            if self.health >= (i + 1) * 2:
                image = self.Full_heart
            elif self.health == i * 2 + 1:
                image = self.Half_heart
            else:
                image = self.Empty_heart

            screen.blit(image, (heart_x + i * spacing, heart_y))

    def set_position(self, x, y):
        self.x = x
        self.y = y