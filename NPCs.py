import pygame
import random

class NPC:
    def __init__(self, x, y):

        self.images = [
            pygame.transform.scale(pygame.image.load("NPCs/PurpleGirl/Standard.png").convert_alpha(), (45, 45)),
            pygame.transform.scale(pygame.image.load("NPCs/PurpleGirl/Blink1.png").convert_alpha(), (45, 45)),
            pygame.transform.scale(pygame.image.load("NPCs/PurpleGirl/Blink2.png").convert_alpha(), (45, 45)),
            pygame.transform.scale(pygame.image.load("NPCs/PurpleGirl/Blink3.png").convert_alpha(), (45, 45)),
        ]

        self.image = self.images[0]

        self.x = x
        self.y = y

        self.blinking = False
        self.blink_start = 0

        self.frame_delay = 60

        # animation order
        self.blink_sequence = [0, 1, 2, 3, 2, 1, 0]
        self.sequence_index = 0

        self.next_blink = pygame.time.get_ticks() + random.randint(500, 3000)

        self.sound = [
            pygame.mixer.Sound("NPCs/Sounds/Sound1.mp3")
        ]

    def update(self):

        current_time = pygame.time.get_ticks()

        # start blink
        if not self.blinking and current_time >= self.next_blink:
            self.blinking = True
            self.blink_start = current_time
            self.sequence_index = 0

        # animate blink
        if self.blinking:

            if current_time - self.blink_start >= self.frame_delay:

                self.blink_start = current_time

                self.image = self.images[self.blink_sequence[self.sequence_index]]

                self.sequence_index += 1

                # animation finished
                if self.sequence_index >= len(self.blink_sequence):

                    self.blinking = False
                    self.image = self.images[0]

                    self.next_blink = current_time + random.randint(2000, 5000)

    def draw(self, screen):
        self.update()
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 45, 45)