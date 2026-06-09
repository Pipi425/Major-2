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
                "Characters_saber/idle_" + direction + ".png",
                SIZE
            )

            self.run[direction] = load_images(
                "Characters_saber/run_" + direction + ".png",
                SIZE
            )

            attack1 = load_images(
                "Characters_saber/attack1_" + direction + ".png",
                SIZE
            )

            attack2 = load_images(
                "Characters_saber/attack2_" + direction + ".png",
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

        self.base_health = 12
        self.health = 12

        self.dead = False

        self.weapon = None
        self.bow = None

        self.head_armor = None
        self.chest_armor = None
        self.hand_armor = None
        self.leg_armor = None

        self.ice_velocity_x = 0
        self.ice_velocity_y = 0

        self.ice_acceleration = 0.08
        self.ice_friction = 0.97
        self.ice_max_speed = 3.5

        # ================= STAMINA =================

        self.max_stamina = 100000
        self.stamina = self.max_stamina

        self.stamina_recharge_delay = 0
        self.exhausted = False

        self.can_attack = False

        self.bow_cooldown = 0
        self.max_bow_cooldown = 1

        self.vel_accum_x = 0.0
        self.vel_accum_y = 0.0

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

        self.attack_cooldown = self.weapon.cooldown * 0.06

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
        return pygame.Rect(self.x + 60, self.y + 88, 20, 18)

    def get_hurt_rect(self):
        return pygame.Rect(
            self.x + 48,
            self.y + 40,
            44,
            72
        )

    def get_center(self):
        image = self.get_image()
        rect = image.get_rect(topleft=(self.x, self.y))
        return rect.center

    def take_hit(self, damage):
        if not self.hit and not self.dead:
            random.choice(self.hurt_sound).play()

            self.hit = True
            self.hit_timer = 30
            self.hit_flash_counter = 0

            self.health -= damage
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

    def move(self, keys, walls, ice_rects):

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.bow_cooldown > 0:
            self.bow_cooldown -= 1

        # ===== STAMINA =====

        if self.exhausted:
            speed = 2

            if self.stamina_recharge_delay > 0:
                self.stamina_recharge_delay -= 1

            else:
                self.stamina += 1

                if self.stamina >= self.max_stamina:
                    self.stamina = self.max_stamina
                    self.exhausted = False

        else:

            running = (
                    keys[pygame.K_LSHIFT]
                    and (
                            keys[pygame.K_w]
                            or keys[pygame.K_a]
                            or keys[pygame.K_s]
                            or keys[pygame.K_d]
                    )
            )

            if running:

                self.stamina -= 1

                if self.stamina <= 0:
                    self.stamina = 0
                    self.exhausted = True

                    self.stamina_recharge_delay = 100

            elif self.stamina < self.max_stamina:

                self.stamina += 1

        # ===== Attack =====
        if keys[pygame.K_q]:  # 如果你想继续用Q攻击
            if keys[pygame.K_q]:

                if not self.can_attack:
                    return  # 或直接 ignore

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

        if (
                keys[pygame.K_LSHIFT]
                and self.stamina > 0
                and not self.exhausted
        ):
            speed = self.fast_speed

        if self.exhausted:
            speed = 2

        # ===== Input =====
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

        # ==========================================
        # ICE SYSTEM
        # ==========================================

        on_ice = self.on_ice(ice_rects)

        if on_ice:

            accel = self.ice_acceleration

            if (
                    keys[pygame.K_LSHIFT]
                    and self.stamina > 0
                    and not self.exhausted
            ):
                accel *= 1.8

            if keys[pygame.K_a]:
                self.ice_velocity_x -= accel

            if keys[pygame.K_d]:
                self.ice_velocity_x += accel

            if keys[pygame.K_w]:
                self.ice_velocity_y -= accel

            if keys[pygame.K_s]:
                self.ice_velocity_y += accel

            max_speed = self.ice_max_speed

            if (
                    keys[pygame.K_LSHIFT]
                    and self.stamina > 0
                    and not self.exhausted
            ):
                max_speed *= 1.5

            self.ice_velocity_x = max(
                -max_speed,
                min(self.ice_velocity_x, max_speed)
            )

            self.ice_velocity_y = max(
                -max_speed,
                min(self.ice_velocity_y, max_speed)
            )

            self.ice_velocity_x *= self.ice_friction
            self.ice_velocity_y *= self.ice_friction

            self.ice_velocity_x = max(
                -max_speed,
                min(self.ice_velocity_x, max_speed)
            )

            self.ice_velocity_y = max(
                -max_speed,
                min(self.ice_velocity_y, max_speed)
            )

            # ===== X =====

            self.vel_accum_x += self.ice_velocity_x

            move_x = int(self.vel_accum_x)

            self.vel_accum_x -= move_x

            if move_x != 0:

                if self.check_move(move_x, 0, walls):
                    self.x += move_x
                    self.moving = True

                else:
                    self.ice_velocity_x = 0
                    self.vel_accum_x = 0

            # ===== Y =====

            self.vel_accum_y += self.ice_velocity_y

            move_y = int(self.vel_accum_y)

            self.vel_accum_y -= move_y

            if move_y != 0:

                if self.check_move(0, move_y, walls):
                    self.y += move_y
                    self.moving = True

                else:
                    self.ice_velocity_y = 0
                    self.vel_accum_y = 0

        # ==========================================
        # NORMAL MOVEMENT
        # ==========================================

        else:

            self.ice_velocity_x = 0
            self.ice_velocity_y = 0

            self.vel_accum_x = 0
            self.vel_accum_y = 0

            if dx != 0:

                if self.check_move(dx, 0, walls):
                    self.x += dx
                    self.moving = True

            if dy != 0:

                if self.check_move(0, dy, walls):
                    self.y += dy
                    self.moving = True

        # ==========================================
        # ANIMATION
        # ==========================================

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

        image = self.get_image()

        screen.blit(image, (self.x, self.y))

        # 蓝框：角色图片
        pygame.draw.rect(
            screen,
            (0, 0, 255),
            image.get_rect(topleft=(self.x, self.y)),
            2
        )

        # 红框：脚底碰撞
        pygame.draw.rect(
            screen,
            (255, 0, 0),
            self.get_rect(),
            2
        )

        # 绿框：受伤判定
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            self.get_hurt_rect(),
            2
        )

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

    def draw_stamina_bar(self, screen):

        x = 25
        y = 80

        width = 200
        height = 16

        ratio = self.stamina / self.max_stamina

        # 背景
        pygame.draw.rect(
            screen,
            (50, 50, 50),
            (x, y, width, height)
        )

        # 颜色
        if ratio > 0.5:
            color = (0, 220, 0)  # 绿

        elif ratio > 0.2:
            color = (255, 140, 0)  # 橙

        else:
            color = (255, 0, 0)  # 红

        pygame.draw.rect(
            screen,
            color,
            (x, y, width * ratio, height)
        )

        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (x, y, width, height),
            2
        )

    def draw_weapon_cooldowns(self, screen):

        x = 25
        y = 110

        icon_size = 32

        bar_width = 100
        bar_height = 12

        if self.weapon:

            icon = pygame.transform.scale(
                self.weapon.image,
                (icon_size, icon_size)
            )

            screen.blit(icon, (x, y))

            max_cd = self.weapon.cooldown * 0.06

            ratio = 1

            if max_cd > 0:
                ratio = 1 - self.attack_cooldown / max_cd

            pygame.draw.rect(
                screen,
                (60, 60, 60),
                (x + 40, y + 10, bar_width, bar_height)
            )

            pygame.draw.rect(
                screen,
                (200, 200, 200),
                (x + 40, y + 10, bar_width * ratio, bar_height)
            )

        if self.bow:

            y += 45

            icon = pygame.transform.scale(
                self.bow.image,
                (icon_size, icon_size)
            )

            screen.blit(icon, (x, y))

            max_cd = self.bow.cooldown * 0.06

            ratio = 1

            if max_cd > 0:
                ratio = 1 - self.bow_cooldown / max_cd

            ratio = max(0, min(1, ratio))

            pygame.draw.rect(
                screen,
                (60, 60, 60),
                (x + 40, y + 10, bar_width, bar_height)
            )

            pygame.draw.rect(
                screen,
                (180, 220, 255),
                (x + 40, y + 10, bar_width * ratio, bar_height)
            )

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