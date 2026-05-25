import pygame
import math


class Chest:
    def __init__(self, x, y):
        self.images = []

        for i in range(4):
            image = pygame.image.load(f"Chests/chest_{i}.png").convert_alpha()
            image = pygame.transform.scale(image, (32, 32))
            self.images.append(image)

        self.music = []
        self.music.append(pygame.mixer.Sound("SoundEffects/Chest_opening_sound.mp3"))
        self.music.append(pygame.mixer.Sound("SoundEffects/Chest_opening_music.mp3"))
        self.music[0].set_volume(0.5)
        self.music[1].set_volume(4.0)

        self.frame = 0
        self.image = self.images[self.frame]

        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = pygame.Rect(x, y, 32, 32)

        self.opened = False
        self.opening = False

        self.animation_timer = 0
        self.animation_speed = 20

        self.show_prompt = False
        self.state = "idle"

        self.loot_item = None
        self.looted = False
        self.give_loot = False

        self.prompt_img = pygame.transform.scale(
            pygame.image.load("Graphics/F.png").convert_alpha(),
            (28, 28)
        )

        self.bob_offset = 0

    def set_loot(self, item):
        self.loot_item = item

    def update(self, player):
        if self.state == "ui_done":
            return

        distance = pygame.Vector2(player.get_center()).distance_to(self.rect.center)
        keys = pygame.key.get_pressed()

        if distance < 80 and not self.opened and self.state == "idle":
            self.show_prompt = True

            if keys[pygame.K_f] and not self.opening:
                self.opening = True
                self.state = "opening"

                self.music[0].play()
                self.music[1].play()
        else:
            self.show_prompt = False

        if self.state == "opening":
            self.animation_timer += 1

            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0

                if self.frame < 3:
                    self.frame += 1
                    self.image = self.images[self.frame]

                if self.frame >= 3:
                    self.opened = True
                    self.opening = False
                    self.state = "opened"

                    if not self.looted:
                        self.looted = True
                        self.give_loot = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)

        if self.show_prompt:
            offset_y = -30 + int((3 * pygame.time.get_ticks() / 300) % 2)

            screen.blit(
                self.prompt_img,
                (
                    self.rect.centerx - self.prompt_img.get_width() // 2,
                    self.rect.y + offset_y
                )
            )

    def draw_loot_ui(self, screen):
        if self.state != "opened" or not self.loot_item:
            return

        panel = pygame.Rect(340, 200, 600, 300)

        pygame.draw.rect(screen, (20, 20, 20), panel, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), panel, 2, border_radius=12)

        img = self.loot_item.image
        img = pygame.transform.scale(img, (140, 140))
        screen.blit(img, (panel.x + 30, panel.y + 80))

        font = pygame.font.SysFont(None, 26)

        max_width = panel.width - 220
        x_text = panel.x + 200
        y_text = panel.y + 80

        words = self.loot_item.description.split(" ")

        line = ""
        for word in words:
            test_line = line + word + " "
            if font.size(test_line)[0] > max_width:
                screen.blit(font.render(line, True, (255, 255, 255)), (x_text, y_text))
                y_text += 32
                line = word + " "
            else:
                line = test_line

        if line:
            screen.blit(font.render(line, True, (255, 255, 255)), (x_text, y_text))

    def close_ui(self):
        self.state = "ui_done"