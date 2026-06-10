import pygame
import math


def load_images(path, frame_count, size):
    sheet = pygame.image.load(path).convert_alpha()

    frames = []

    frame_width = sheet.get_width() // frame_count
    frame_height = sheet.get_height()

    for i in range(frame_count):
        frame = sheet.subsurface(
            pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        ).copy()

        frame = pygame.transform.scale(frame, size)

        frames.append(frame)

    return frames


class Bone:
    def __init__(self, x, y, dx, dy, images):
        self.x = x
        self.y = y

        self.dx = dx
        self.dy = dy

        self.images = images
        self.frame = 0
        self.animation_count = 0

        self.speed = 7
        self.damage = 2
        self.lifetime = 170

    def get_rect(self):
        return pygame.Rect(self.x + 75, self.y + 75, 50, 50)

    def update_animation(self):
        self.animation_count += 1

        if self.animation_count >= 5:
            self.animation_count = 0
            self.frame += 1

            if self.frame >= len(self.images):
                self.frame = 0

    def update(self, player, walls):

        player_rect = player.get_rect()

        target_dx = player_rect.centerx - (self.x + 100)
        target_dy = player_rect.centery - (self.y + 100)

        distance = math.sqrt(
            target_dx * target_dx +
            target_dy * target_dy
        )

        if distance != 0:
            self.dx = target_dx / distance
            self.dy = target_dy / distance

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        self.lifetime -= 1
        self.update_animation()

        for wall in walls:
            if self.get_rect().colliderect(wall):
                return False

        if self.get_rect().colliderect(player.get_hurt_rect()):
            self.hit_player(player)
            return False

        if self.lifetime <= 0:
            return False

        return True

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

    def draw(self, screen):
        image = self.images[self.frame]

        if self.dx < 0:
            image = pygame.transform.flip(image, True, False)

        screen.blit(image, (self.x, self.y))

        pygame.draw.rect(
            screen,
            (0, 0, 255),
            image.get_rect(topleft=(self.x, self.y)),
            2
        )


class SecondBoss:
    def __init__(self, x, y):

        # animations
        BOSS_SIZE = (400, 400)

        self.idle = load_images("BoneBoss/idle.png", 10, BOSS_SIZE)
        self.walk = load_images("BoneBoss/walk.png", 6, BOSS_SIZE)
        self.attack = load_images("BoneBoss/attack.png", 10, BOSS_SIZE)
        self.hurt = load_images("BoneBoss/hurt.png", 5, BOSS_SIZE)
        self.die = load_images("BoneBoss/death.png", 7, BOSS_SIZE)

        self.bone_images = load_images("BoneBoss/bone.png", 3, (200, 200))

        # position
        self.x = x
        self.y = y

        # animation
        self.frame = 0
        self.animation_count = 0

        # state
        self.state = "idle"
        self.flip = False

        # hp
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.dead_done = False

        # movement
        self.speed = 2
        self.speed_count = 0

        # attack
        self.attack_cooldown = 0
        self.attack_time = 0
        self.bone_thrown = False
        self.bones = []

        # hurt
        self.hurt_time = 0

    def get_rect(self):
        return pygame.Rect(
            self.x + 135,
            self.y + 130,
            130,
            120
        )

    def update_animation(self, speed):
        images = self.get_current_images()

        if len(images) == 0:
            return

        self.animation_count += 1

        if self.animation_count >= speed:
            self.animation_count = 0
            self.frame += 1

            if self.frame >= len(images):

                if self.state == "die":
                    self.frame = len(images) - 1
                    self.dead_done = True

                elif self.state == "attack":
                    self.frame = len(images) - 1

                else:
                    self.frame = 0

    def throw_bone(self, player):
        player_rect = player.get_rect()
        boss_rect = self.get_rect()

        dx = player_rect.centerx - boss_rect.centerx
        dy = player_rect.centery - boss_rect.centery

        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            distance = 1

        dx = dx / distance
        dy = dy / distance

        bone_x = boss_rect.centerx - 100
        bone_y = boss_rect.centery - 100

        self.bones.append(
            Bone(bone_x, bone_y, dx, dy, self.bone_images)
        )

    def update_bones(self, player, walls):
        for bone in self.bones[:]:
            alive = bone.update(player, walls)

            if not alive:
                self.bones.remove(bone)

    def move_with_collision(self, move_x, move_y, walls):
        old_x = self.x
        old_y = self.y


        self.x += move_x
        boss_rect = self.get_rect()

        for wall in walls:
            if boss_rect.colliderect(wall):
                self.x = old_x
                break


        self.y += move_y
        boss_rect = self.get_rect()

        for wall in walls:
            if boss_rect.colliderect(wall):
                self.y = old_y
                break


        if self.x == old_x and self.y == old_y:
            self.x -= move_x
            self.y -= move_y

    def move(self, player, walls):

        self.update_bones(player, walls)

        if not self.alive:
            self.state = "die"
            self.update_animation(7)
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.state == "hurt":
            self.hurt_time -= 1

            if self.hurt_time <= 0:
                self.state = "idle"

            self.update_animation(5)
            return

        player_rect = player.get_rect()
        boss_rect = self.get_rect()

        dx = player_rect.centerx - boss_rect.centerx
        dy = player_rect.centery - boss_rect.centery

        distance = math.sqrt(dx * dx + dy * dy)

        if dx < 0:
            self.flip = True
        else:
            self.flip = False

        if self.state == "attack":
            self.attack_time -= 1
            self.update_animation(4)

            if self.attack_time <= 25 and not self.bone_thrown:
                self.throw_bone(player)
                self.bone_thrown = True

            if self.attack_time <= 0:
                self.state = "idle"
                self.frame = 0
                self.animation_count = 0

            return

        # start throwing bone
        if distance < 550 and distance > 180 and self.attack_cooldown <= 0:
            self.state = "attack"
            self.frame = 0
            self.animation_count = 0

            self.attack_time = 45
            self.attack_cooldown = 90
            self.bone_thrown = False

            return

        # follow player if too far
        if distance > 300 and distance < 800:
            self.state = "walk"

            if distance == 0:
                distance = 1

            move_x = dx / distance * self.speed
            move_y = dy / distance * self.speed

            self.move_with_collision(move_x, move_y, walls)

            self.update_animation(6)
            return

        # move away if player is too close
        if distance < 180:
            self.state = "walk"

            if distance == 0:
                distance = 1

            move_x = -dx / distance * self.speed
            move_y = -dy / distance * self.speed

            self.move_with_collision(move_x, move_y, walls)

            self.update_animation(6)
            return

        self.state = "idle"
        self.update_animation(7)

    def hit(self, damage):
        if not self.alive:
            return

        self.hp -= damage

        self.state = "hurt"
        self.frame = 0
        self.animation_count = 0
        self.hurt_time = 18

        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.state = "die"
            self.frame = 0
            self.animation_count = 0

    def draw_health_bar(self, screen):
        if not self.alive:
            return

        bar_x = self.x + 125
        bar_y = self.y + 100

        width = 150
        height = 12

        current_width = width * (self.hp / self.max_hp)

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            (bar_x, bar_y, width, height)
        )

        pygame.draw.rect(
            screen,
            (180, 30, 30),
            (bar_x, bar_y, current_width, height)
        )

    def get_current_images(self):
        if self.state == "idle":
            images = self.idle

        elif self.state == "walk":
            images = self.walk

        elif self.state == "attack":
            images = self.attack

        elif self.state == "hurt":
            images = self.hurt

        else:
            images = self.die

        if len(images) == 0:
            return []

        if self.frame >= len(images):
            self.frame = 0

        if self.frame < 0:
            self.frame = 0

        return images

    def draw(self, screen):
        images = self.get_current_images()

        if len(images) == 0:
            return

        image = images[self.frame]

        if self.flip:
            image = pygame.transform.flip(image, True, False)

        screen.blit(image, (self.x, self.y))

        pygame.draw.rect(
            screen,
            (255, 0, 0),
            self.get_rect(),
            2
        )

        self.draw_health_bar(screen)

        for bone in self.bones:
            bone.draw(screen)

            pygame.draw.rect(
                screen,
                (0, 255, 0),
                bone.get_rect(),
                2
            )