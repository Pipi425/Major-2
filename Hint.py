import pygame


class HintAnimation:
    def __init__(
            self,
            x,
            y,
            frame_duration=100,
            pause_duration=1000,
            hidden_duration=2000
    ):
        self.x = x
        self.y = y

        self.frames = []

        for i in range(1, 8):
            img = pygame.image.load(
                f"Graphics/Hint/keyhint{i}.png"
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                (
                    img.get_width() * 3,
                    img.get_height() * 3
                )
            )

            self.frames.append(img)

        self.frame_duration = frame_duration
        self.pause_duration = pause_duration
        self.hidden_duration = hidden_duration

        self.frame_index = 0
        self.last_time = pygame.time.get_ticks()

        # states:
        # playing
        # pause
        # hidden

        self.state = "playing"

    def update(self):

        now = pygame.time.get_ticks()

        # ================= PLAYING =================

        if self.state == "playing":

            if now - self.last_time >= self.frame_duration:

                self.frame_index += 1
                self.last_time = now

                if self.frame_index >= len(self.frames):

                    self.frame_index = len(self.frames) - 1
                    self.state = "pause"
                    self.last_time = now

        # ================= PAUSE =================

        elif self.state == "pause":

            if now - self.last_time >= self.pause_duration:

                self.state = "hidden"
                self.last_time = now

        # ================= HIDDEN =================

        elif self.state == "hidden":

            if now - self.last_time >= self.hidden_duration:

                self.state = "playing"
                self.frame_index = 0
                self.last_time = now

    def draw(self, screen):

        if self.state != "hidden":

            screen.blit(
                self.frames[self.frame_index],
                (self.x, self.y)
            )