import pygame
import math
import random



def load_images(path, frame_count):
    sheet = pygame.image.load(path).convert_alpha()

    frames = []

    frame_width = sheet.get_width() // frame_count
    frame_height = sheet.get_height()

    for i in range(frame_count):
        frame = sheet.subsurface(
            pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        )

        frame = pygame.transform.scale(frame, (330, 270))

        frames.append(frame)

    return frames


class Boss:
    def __init__(self, x, y):

        #animations
        self.idle = load_images("Bosses/Golem_1_idle.png", 8)
        self.walk = load_images("Bosses/Golem_1_walk.png", 10)
        self.attack = load_images("Bosses/Golem_1_attack.png", 11)
        self.hurt = load_images("Bosses/Golem_1_hurt.png", 4)
        self.die = load_images("Bosses/Golem_1_die.png", 13)

        #position
        self.x = x
        self.y = y

        #animation
        self.frame = 0
        self.animation_count = 0

        #state
        self.state = "idle"

        #hp
        self.hp = 100
        self.alive = True
        self.dead_done = False

        #movement
        self.speed = 2
        self.charge_speed = 10

        #attack
        self.attack_cooldown = 0
        self.attack_delay = 0
        self.charge_time = 0

        self.charge_x = 0
        self.charge_y = 0

        #hurt
        self.hurt_time = 0

        # anti-stuck pathfinding
        self.stuck_timer = 0

        self.pathfinding_time = 0
        self.pathfinding_x = 0
        self.pathfinding_y = 0

        # boss intro
        self.intro_timer = 90

        self.death_sound_played = False

        self.sounds = []

        self.HurtSounds = []

        self.hurt_sound_played = False

        for i in range(5):
            self.sounds.append(pygame.mixer.Sound(f"Bosses/Sounds/Roar{i}.mp3"))
            self.sounds[i].set_volume(0.5)
            if i > 0:
                self.HurtSounds.append(pygame.mixer.Sound(f"HurtSounds/Boss1/Stone{i}.mp3"))

    def get_rect(self):
        return pygame.Rect(self.x + 85, self.y + 130, 160, 140)

    def get_wall_rect(self):
        return pygame.Rect(
            self.x + 130,
            self.y + 210,
            70,
            50
        )

    def update_animation(self, speed):

        self.animation_count += 1

        if self.animation_count >= speed:

            self.animation_count = 0
            self.frame += 1

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

            if self.frame >= len(images):

                if self.state == "die":
                    self.frame = len(images) - 1
                    self.dead_done = True

                else:
                    self.frame = 0

    def move(self, player, walls):

        if not self.alive:

            self.state = "die"
            self.update_animation(6)

            if not self.death_sound_played:
                random.choice(self.sounds).play()
                self.death_sound_played = True

            return

        # ================= INTRO =================

        if self.intro_timer > 0:
            self.intro_timer -= 1

            self.state = "idle"

            self.update_animation(8)

            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # ================= HURT =================

        if self.state == "hurt":

            if not self.hurt_sound_played:

                if self.HurtSounds:
                    random.choice(self.HurtSounds).play()

                self.hurt_sound_played = True

            self.hurt_time -= 1

            if self.hurt_time <= 0:
                self.state = "idle"

            self.update_animation(6)
            return

        # ================= PATHFINDING MODE =================

        if self.pathfinding_time > 0:

            self.pathfinding_time -= 1

            move_x = self.pathfinding_x * self.speed
            move_y = self.pathfinding_y * self.speed

            test_rect = self.get_wall_rect().move(move_x, move_y)

            if not any(test_rect.colliderect(w) for w in walls):
                self.x += move_x
                self.y += move_y

            self.state = "walk"
            self.update_animation(6)

            return

        player_rect = player.get_rect()
        boss_rect = self.get_rect()

        dx = player_rect.centerx - boss_rect.centerx
        dy = player_rect.centery - boss_rect.centery

        distance = math.sqrt(dx * dx + dy * dy)


        # ================= ATTACK =================

        if self.state == "attack":

            self.update_animation(4)

            if self.attack_delay > 0:
                self.attack_delay -= 1
                return

            if self.charge_time > 0:

                move_x = self.charge_x * self.charge_speed
                move_y = self.charge_y * self.charge_speed

                # X
                new_rect = self.get_wall_rect().move(move_x, 0)

                if not any(new_rect.colliderect(w) for w in walls):
                    self.x += move_x
                else:
                    move_x = 0

                # Y
                new_rect = self.get_wall_rect().move(0, move_y)

                if not any(new_rect.colliderect(w) for w in walls):
                    self.y += move_y
                else:
                    move_y = 0

                if move_x == 0 and move_y == 0:
                    self.charge_time = 0
                    self.state = "idle"
                    self.frame = 0
                    return

                self.charge_time -= 1
                return

            self.state = "idle"
            self.frame = 0
            return

        # ================= START ATTACK =================

        if distance < 220 and self.attack_cooldown <= 0:

            random.choice(self.sounds).play()

            self.state = "attack"

            self.frame = 0
            self.animation_count = 0

            self.attack_delay = 40
            self.charge_time = 25
            self.attack_cooldown = 120

            if distance == 0:
                distance = 1

            self.charge_x = dx / distance
            self.charge_y = dy / distance

            return

        # ================= FOLLOW PLAYER =================

        self.state = "walk"

        if distance == 0:
            distance = 1

        move_x = dx / distance * self.speed
        move_y = dy / distance * self.speed

        if abs(dx) > abs(dy):
            preferred_axis = "x"
        else:
            preferred_axis = "y"

        moved = False

        # ---------- X ----------
        test_rect = self.get_wall_rect().move(move_x, 0)

        if not any(test_rect.colliderect(w) for w in walls):
            self.x += move_x
            moved = True

        # ---------- Y ----------
        test_rect = self.get_wall_rect().move(0, move_y)

        if not any(test_rect.colliderect(w) for w in walls):
            self.y += move_y
            moved = True

        # ---------- STUCK CHECK ----------

        if moved:

            self.stuck_timer = 0

        else:

            self.stuck_timer += 1

            if self.stuck_timer > 10:

                # 想横向追玩家却被卡住
                if preferred_axis == "x":

                    if dy < 0:
                        directions = [
                            (0, -1),
                            (0, 1)
                        ]
                    else:
                        directions = [
                            (0, 1),
                            (0, -1)
                        ]

                # 想纵向追玩家却被卡住
                else:

                    if dx < 0:
                        directions = [
                            (-1, 0),
                            (1, 0)
                        ]
                    else:
                        directions = [
                            (1, 0),
                            (-1, 0)
                        ]

                for dir_x, dir_y in directions:

                    test_rect = self.get_wall_rect().move(
                        dir_x * self.speed * 15,
                        dir_y * self.speed * 15
                    )

                    if not any(test_rect.colliderect(w) for w in walls):
                        self.pathfinding_x = dir_x
                        self.pathfinding_y = dir_y

                        # 绕路时间
                        self.pathfinding_time = 90

                        self.stuck_timer = 0

                        break

        self.update_animation(6)

    def hit(self, damage):

        if not self.alive:
            return

        self.hp -= damage

        self.state = "hurt"

        self.frame = 0
        self.animation_count = 0

        self.hurt_time = 20

        self.hurt_sound_played = False

        if self.hp <= 0:
            self.hp = 0
            self.alive = False

            self.state = "die"

            self.frame = 0
            self.animation_count = 0

    def draw_health_bar(self, screen):

        if not self.alive:
            return

        bar_x = self.x + 115
        bar_y = self.y + 90

        width = 100
        height = 10

        current_width = width * (self.hp / 100)

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

    def draw(self, screen):

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

        image = images[self.frame]

        screen.blit(image, (self.x, self.y))

        self.draw_health_bar(screen)
