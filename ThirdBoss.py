import pygame
import math


DIRECTIONS = ["down", "up", "left", "right"]


def load_images(path, frame_count, size):
    sheet = pygame.image.load(path).convert_alpha()
    images = []

    frame_width = sheet.get_width() // frame_count
    frame_height = sheet.get_height()

    for i in range(frame_count):
        image = sheet.subsurface(
            pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        ).copy()

        image = pygame.transform.scale(image, size)
        images.append(image)

    return images


def load_action(folder, boss_name, action_name, frame_count, size):
    images = {}

    for direction in DIRECTIONS:
        big_direction = direction.capitalize()
        path = "Bosses/" + folder + "/" + boss_name + big_direction + action_name + ".png"
        images[direction] = load_images(path, frame_count, size)

    return images


class ThirdBoss:
    def __init__(self, x, y):
        self.phase1_images = {
            "idle": load_action("AncientSkeleton", "AncientSkeleton", "Idle", 7, (150, 150)),
            "walk": load_action("AncientSkeleton", "AncientSkeleton", "Walk", 8, (150, 150)),
            "attack1": load_action("AncientSkeleton", "AncientSkeleton", "Attack01", 7, (150, 150)),
            "attack2": load_action("AncientSkeleton", "AncientSkeleton", "Attack02", 13, (150, 150)),
            "attack3": load_action("AncientSkeleton", "AncientSkeleton", "Attack03", 7, (150, 150)),
            "hurt": load_action("AncientSkeleton", "AncientSkeleton", "Hurt", 4, (150, 150)),
            "die": load_action("AncientSkeleton", "AncientSkeleton", "Death", 9, (150, 150)),
            "jump": load_action("AncientSkeleton", "AncientSkeleton", "Jump", 5, (150, 150)),
            "land": load_action("AncientSkeleton", "AncientSkeleton", "Land", 4, (150, 150))
        }

        self.phase2_images = {
            "idle": load_action("SkeletonKing", "SkeletonKing", "Idle", 6, (150, 150)),
            "walk": load_action("SkeletonKing", "SkeletonKing", "Walk", 10, (150, 150)),
            "attack1": load_action("SkeletonKing", "SkeletonKing", "Attack01", 10, (200, 200)),
            "attack2": load_action("SkeletonKing", "SkeletonKing", "Attack02", 4, (300, 300)),
            "attack3": load_action("SkeletonKing", "SkeletonKing", "Attack03", 12, (200, 200)),
            "hurt": load_action("SkeletonKing", "SkeletonKing", "Hurt", 4, (150, 150)),
            "die": load_action("SkeletonKing", "SkeletonKing", "Death", 13, (150, 150)),
            "jump": load_action("SkeletonKing", "SkeletonKing", "Jump", 6, (150, 150)),
            "land": load_action("SkeletonKing", "SkeletonKing", "Land", 4, (150, 150))
        }

        self.x = x
        self.y = y

        self.phase = 1
        self.state = "idle"
        self.direction = "down"

        self.frame = 0
        self.frame_count = 0

        self.hp = 25
        self.max_hp = 25

        self.alive = True
        self.dead_done = False

        self.speed = 1.3
        self.jump_speed = 5
        self.detect_range = 600

        self.attack_range = 110
        self.attack_cooldown = 0
        self.attack_count = 0
        self.damage = 2
        self.damage_done = False

        self.jump_cooldown = 0
        self.jump_time = 0
        self.land_time = 0
        self.jump_dx = 0
        self.jump_dy = 0

        self.hurt_time = 0

    def set_state(self, state):
        self.state = state
        self.frame = 0
        self.frame_count = 0
        self.damage_done = False

    def get_images(self):
        if self.phase == 1:
            images = self.phase1_images[self.state][self.direction]
        else:
            images = self.phase2_images[self.state][self.direction]

        if self.frame >= len(images):
            self.frame = 0

        return images

    def play_animation(self, speed):
        images = self.get_images()

        if self.phase == 2 and self.state != "die":
            speed -= 1

            if speed < 3:
                speed = 3

        self.frame_count += 1

        if self.frame_count < speed:
            return False

        self.frame_count = 0
        self.frame += 1

        if self.frame < len(images):
            return False

        if self.state == "die":
            self.frame = len(images) - 1
            self.dead_done = True

        elif self.state in ["attack1", "attack2", "attack3", "jump", "land"]:
            self.frame = len(images) - 1

        else:
            self.frame = 0

        return True

    def get_player_distance(self, player):
        player_rect = player.get_rect()
        boss_rect = self.get_rect()

        dx = player_rect.centerx - boss_rect.centerx
        dy = player_rect.centery - boss_rect.centery

        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            distance = 1

        return dx, dy, distance

    def face_player(self, dx, dy):
        if abs(dx) > abs(dy):
            if dx < 0:
                self.direction = "left"
            else:
                self.direction = "right"
        else:
            if dy < 0:
                self.direction = "up"
            else:
                self.direction = "down"

    def get_rect(self):
        if self.phase == 1:
            return pygame.Rect(self.x + 58, self.y + 78, 35, 35)

        return pygame.Rect(self.x + 55, self.y + 75, 40, 38)

    def get_hurt_rect(self):
        if self.phase == 1:
            return pygame.Rect(self.x + 50, self.y + 45, 50, 75)

        return pygame.Rect(self.x + 48, self.y + 50, 55, 75)

    def get_attack_rect(self):
        boss_rect = self.get_rect()

        if self.direction == "down":
            return pygame.Rect(boss_rect.centerx - 28, boss_rect.bottom, 56, 42)

        if self.direction == "up":
            return pygame.Rect(boss_rect.centerx - 28, boss_rect.top - 42, 56, 42)

        if self.direction == "left":
            return pygame.Rect(boss_rect.left - 50, boss_rect.centery - 24, 50, 48)

        return pygame.Rect(boss_rect.right, boss_rect.centery - 24, 50, 48)

    def move_and_check_wall(self, move_x, move_y, walls):
        old_x = self.x
        old_y = self.y

        self.x += move_x

        for wall in walls:
            if self.get_rect().colliderect(wall):
                self.x = old_x
                break

        self.y += move_y

        for wall in walls:
            if self.get_rect().colliderect(wall):
                self.y = old_y
                break

    def walk_to_player(self, dx, dy, distance, walls):
        self.state = "walk"

        move_x = dx / distance * self.speed
        move_y = dy / distance * self.speed

        self.move_and_check_wall(move_x, move_y, walls)
        self.play_animation(6)

    def start_attack(self):
        self.attack_count += 1

        if self.attack_count % 3 == 1:
            self.set_state("attack1")
        elif self.attack_count % 3 == 2:
            self.set_state("attack2")
        else:
            self.set_state("attack3")

        if self.phase == 1:
            self.attack_cooldown = 110
        else:
            self.attack_cooldown = 75

    def start_jump_attack(self, dx, dy, distance):
        self.set_state("jump")

        self.jump_dx = dx / distance
        self.jump_dy = dy / distance

        if self.phase == 1:
            self.jump_time = 25
            self.land_time = 20
            self.jump_cooldown = 180
        else:
            self.jump_time = 22
            self.land_time = 15
            self.jump_cooldown = 120

    def check_hit_player(self, player):
        if self.damage_done:
            return

        if self.state not in ["attack1", "attack2", "attack3", "land"]:
            return

        images = self.get_images()
        hit_frame = len(images) // 2

        if self.frame != hit_frame:
            return

        player_rect = player.get_hurt_rect()

        if self.get_attack_rect().colliderect(player_rect):
            self.hit_player(player)
            self.damage_done = True

    def hit_player(self, player):
        if player.hit:
            return

        player.health -= self.damage
        player.hp = player.health

        player.hit = True
        player.hit_timer = 60
        player.hit_flash_counter = 0

        if player.health <= 0:
            player.health = 0
            player.hp = 0
            player.dead = True

        if len(player.hurt_sound) > 0:
            player.hurt_sound[0].play()

    def count_cooldown(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

    def start_phase_two(self):
        self.phase = 2

        self.hp = 35
        self.max_hp = 35

        self.speed = 1.8
        self.jump_speed = 7
        self.detect_range = 700
        self.attack_range = 120
        self.damage = 3

        self.attack_cooldown = 75
        self.jump_cooldown = 100

        self.set_state("hurt")
        self.hurt_time = 50

    def hit(self):
        if not self.alive:
            return

        self.hp -= 1

        if self.hp <= 0:
            if self.phase == 1:
                self.start_phase_two()
                return

            self.hp = 0
            self.alive = False
            self.set_state("die")
            return

        self.set_state("hurt")

        if self.phase == 1:
            self.hurt_time = 18
        else:
            self.hurt_time = 12

    def move(self, player, walls):
        if not self.alive:
            self.state = "die"
            self.play_animation(7)
            return

        self.count_cooldown()

        if self.state == "hurt":
            self.hurt_time -= 1
            self.play_animation(5)

            if self.hurt_time <= 0:
                self.set_state("idle")

            return

        dx, dy, distance = self.get_player_distance(player)
        self.face_player(dx, dy)

        if self.state in ["attack1", "attack2", "attack3"]:
            self.check_hit_player(player)

            if self.play_animation(6):
                self.set_state("idle")

            return

        if self.state == "jump":
            self.jump_time -= 1

            move_x = self.jump_dx * self.jump_speed
            move_y = self.jump_dy * self.jump_speed

            self.move_and_check_wall(move_x, move_y, walls)
            self.play_animation(5)

            if self.jump_time <= 0:
                self.set_state("land")

            return

        if self.state == "land":
            self.land_time -= 1
            self.check_hit_player(player)

            if self.land_time <= 0 or self.play_animation(5):
                self.set_state("idle")

            return

        if distance < self.attack_range and self.attack_cooldown <= 0:
            self.start_attack()
            return

        if distance > 180 and distance < 380 and self.jump_cooldown <= 0:
            self.start_jump_attack(dx, dy, distance)
            return

        if distance < self.detect_range:
            self.walk_to_player(dx, dy, distance, walls)
            return

        self.state = "idle"
        self.play_animation(7)

    def draw_health_bar(self, screen):
        if not self.alive:
            return

        bar_x = self.x + 10
        bar_y = self.y - 15

        width = 130
        height = 10

        current_width = width * self.hp / self.max_hp

        if self.phase == 1:
            color = (180, 30, 30)
        else:
            color = (160, 40, 200)

        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, width, height))
        pygame.draw.rect(screen, color, (bar_x, bar_y, current_width, height))

    def draw(self, screen):
        images = self.get_images()
        image = images[self.frame]

        if self.phase == 2 and self.alive:
            image = image.copy()
            image.fill((35, 0, 45, 0), special_flags=pygame.BLEND_RGBA_ADD)

        draw_x = self.x + 75 - image.get_width() // 2
        draw_y = self.y + 150 - image.get_height()

        screen.blit(image, (draw_x, draw_y))
        self.draw_health_bar(screen)