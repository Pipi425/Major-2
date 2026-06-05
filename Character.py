import pygame
import random

class Player:
    def __init__(self, spawn_x, spawn_y):
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

        self.x = spawn_x
        self.y = spawn_y
        self.direction = "down"
        self.frame = 0
        self.count = 0
        self.speed = 2
        self.counter = 0

        self.base_speed = 2

        self.ice_velocity_x = 0
        self.ice_velocity_y = 0

        self.ice_acceleration = 0.08
        self.ice_friction = 0.97
        self.ice_max_speed = 3.5

        self.vel_accum_x = 0.0
        self.vel_accum_y = 0.0

        self.base_health = 12
        self.health = 12

        self.dead = False

        self.weapon = None
        self.bow = None

        self.head_armor = None
        self.chest_armor = None
        self.hand_armor = None
        self.leg_armor = None

        self.Full_heart = pygame.transform.scale(
            pygame.image.load("HealthBars/Full_heart.png").convert_alpha(), (40, 40)
        )
        self.Half_heart = pygame.transform.scale(
            pygame.image.load("HealthBars/Half_heart.png").convert_alpha(), (40, 40)
        )
        self.Empty_heart = pygame.transform.scale(
            pygame.image.load("HealthBars/Empty_heart.png").convert_alpha(), (40, 40)
        )

    def get_image(self):
        normal = self.animations[self.direction][self.frame]

        if not self.hit:
            return normal

        if (self.hit_flash_counter // 5) % 2 == 0:
            return normal
        else:
            return self.hit_animations[self.direction][self.frame]

    def get_rect(self):
        return pygame.Rect(self.x + 10, self.y + 32, 20, 15)

    def get_hurt_rect(self):
        return pygame.Rect(self.x, self.y, 45, 45)

    def get_center(self):
        image = self.get_image()
        rect = image.get_rect(topleft=(self.x, self.y))
        return rect.center

    def take_hit(self):
        if not self.hit and not self.dead:
            random.choice(self.hurt_sound).play()
            self.hit = True
            self.hit_timer = 30

            self.health -= 1
            if self.health <= 0:
                self.health = 0
                self.dead = True

    def check_move(self, dx, dy, walls):
        test_rect = self.get_rect()
        test_rect = test_rect.move(dx, dy)
        for wall in walls:
            if test_rect.colliderect(wall):
                return False
        return True

    def move(self, keys, walls, ice_rects):
        moving = False
        dx = 0
        dy = 0
        ICE_MOVE_THRESHOLD = 0.05

        on_ice = self.on_ice(ice_rects)

        # ===== input =====
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

        # =========================
        # ICE MOVEMENT (SMOOTH VERSION)
        # =========================
        if on_ice:

            # acceleration
            if keys[pygame.K_a]:
                self.ice_velocity_x -= self.ice_acceleration
            if keys[pygame.K_d]:
                self.ice_velocity_x += self.ice_acceleration
            if keys[pygame.K_w]:
                self.ice_velocity_y -= self.ice_acceleration
            if keys[pygame.K_s]:
                self.ice_velocity_y += self.ice_acceleration

            # friction
            self.ice_velocity_x *= self.ice_friction
            self.ice_velocity_y *= self.ice_friction

            # clamp
            self.ice_velocity_x = max(-self.ice_max_speed, min(self.ice_velocity_x, self.ice_max_speed))
            self.ice_velocity_y = max(-self.ice_max_speed, min(self.ice_velocity_y, self.ice_max_speed))

            # ===== X axis (smooth + safe) =====
            self.vel_accum_x += self.ice_velocity_x

            move_x = int(self.vel_accum_x)
            self.vel_accum_x -= move_x

            if move_x != 0:
                step_x = 1 if move_x > 0 else -1
                if self.check_move(move_x, 0, walls):
                    self.x += move_x
                    moving = True
                else:
                    self.ice_velocity_x = 0
                    self.vel_accum_x = 0

            # ===== Y axis (smooth + safe) =====
            self.vel_accum_y += self.ice_velocity_y

            move_y = int(self.vel_accum_y)
            self.vel_accum_y -= move_y

            if move_y != 0:
                step_y = 1 if move_y > 0 else -1
                if self.check_move(0, move_y, walls):
                    self.y += move_y
                    moving = True
                else:
                    self.ice_velocity_y = 0
                    self.vel_accum_y = 0

        # =========================
        # NORMAL MOVEMENT
        # =========================
        else:
            self.ice_velocity_x = 0
            self.ice_velocity_y = 0
            self.vel_accum_x = 0
            self.vel_accum_y = 0

            if dx != 0 and self.check_move(dx, 0, walls):
                self.x += dx
                moving = True

            if dy != 0 and self.check_move(0, dy, walls):
                self.y += dy
                moving = True

        # =========================
        # ANIMATION
        # =========================
        if moving or dx != 0 or dy != 0:
            self.count += 1
            self.counter += 1

            if self.counter >= 20:
                random.choice(self.walk_sound).play()
                self.counter = 0

            if self.count >= 10:
                self.count = 0
                self.frame = (self.frame + 1) % 3
        else:
            self.count = 0
            self.frame = 1

        # =========================
        # HIT
        # =========================
        if self.hit:
            self.hit_timer -= 1
            self.hit_flash_counter += 1

            if self.hit_timer <= 0:
                self.hit = False
                self.hit_flash_counter = 0

    def draw(self, screen):
        screen.blit(self.get_image(), (self.x, self.y))

    def draw_health_bar(self, screen):
        heart_x = 20
        heart_y = 20
        spacing = 40

        for i in range(self.max_health // 2):
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

    def on_ice(self, ice_rects):
        player_rect = self.get_rect()

        for ice in ice_rects:
            if player_rect.colliderect(ice):
                return True

        return False

    @property
    def defense(self):
        total = 0

        if self.head_armor:
            total += self.head_armor.defense

        if self.chest_armor:
            total += self.chest_armor.defense

        if self.hand_armor:
            total += self.hand_armor.defense

        if self.leg_armor:
            total += self.leg_armor.defense

        return total

    @property
    def max_health(self):
        return self.base_health + self.defense