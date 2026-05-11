import pygame

class DialogueSystem:
    def __init__(self):
        self.active = False

        self.lines = []
        self.index = 0

        self.display_text = ""
        self.char_index = 0

        self.timer = 0
        self.speed = 2

        self.finished_line = False

    def start(self, lines):
        self.active = True
        self.lines = lines
        self.index = 0

        self.display_text = ""
        self.char_index = 0
        self.finished_line = False

    def update(self):
        if not self.active:
            return

        if self.index >= len(self.lines):
            self.active = False
            return

        line = self.lines[self.index]

        if self.char_index < len(line):
            self.timer += 1
            if self.timer >= self.speed:
                self.display_text += line[self.char_index]
                self.char_index += 1
                self.timer = 0
        else:
            self.finished_line = True

    def next_line(self):
        if not self.active:
            return

        if not self.finished_line:
            self.display_text = self.lines[self.index]
            self.char_index = len(self.lines[self.index])
            self.finished_line = True
            return

        self.index += 1
        self.display_text = ""
        self.char_index = 0
        self.timer = 0
        self.finished_line = False

    def draw(self, screen):
        if not self.active:
            return

        pygame.draw.rect(screen, (0, 0, 0), (0, 500, 1280, 268))
        pygame.draw.rect(screen, (255, 255, 255), (0, 500, 1280, 268), 3)

        font = pygame.font.SysFont(None, 36)

        text_surface = font.render(self.display_text, True, (255, 255, 255))
        screen.blit(text_surface, (50, 550))