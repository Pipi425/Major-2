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

    def draw_text(self, screen, text, font, color, x, y, max_width):
        words = text.split(' ')

        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "

            width = font.size(test_line)[0]

            if width < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        lines.append(current_line)

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)

            screen.blit(
                text_surface,
                (x, y + i * 40)
            )

    def draw(self, screen):
        if not self.active:
            return

        box_x = 40
        box_y = 500
        box_width = 1200
        box_height = 180

        dialogue_surface = pygame.Surface(
            (box_width, box_height),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            dialogue_surface,
            (50, 30, 15, 220),
            (0, 0, box_width, box_height),
            border_radius=20
        )

        screen.blit(dialogue_surface, (box_x, box_y))

        pygame.draw.rect(
            screen,
            (160, 110, 60),
            (box_x, box_y, box_width, box_height),
            4,
            border_radius=20
        )

        font = pygame.font.SysFont(None, 36)

        self.draw_text(
            screen,
            self.display_text,
            font,
            (230, 220, 200),
            box_x + 30,
            box_y + 30,
            box_width - 60
        )