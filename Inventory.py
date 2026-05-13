import pygame


class Item:
    def __init__(self, name, image_path):
        self.name = name
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))


class Inventory:
    def __init__(self, cols=5, rows=3):
        self.cols = cols
        self.rows = rows
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]

    def add_item(self, item):
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y][x] is None:
                    self.grid[y][x] = item
                    return True
        return False


class InventoryUI:
    def __init__(self, inventory, player, screen_width=1280, screen_height=768):

        self.inv = inventory
        self.player = player

        self.slot_size = 64
        self.padding = 10

        self.cursor_x = 0
        self.cursor_y = 0

        self.open = False

        self.grid_width = self.inv.cols * self.slot_size + (self.inv.cols - 1) * self.padding
        self.grid_height = self.inv.rows * self.slot_size + (self.inv.rows - 1) * self.padding

        self.panel_w = 220

        total_width = self.panel_w + self.grid_width + self.panel_w
        self.x = (screen_width - total_width) // 2
        self.y = (screen_height - self.grid_height) // 2

        self.left_x = self.x
        self.grid_x = self.x + self.panel_w + 20
        self.right_x = self.grid_x + self.grid_width + 20

    def move_cursor(self, dx, dy):
        self.cursor_x = (self.cursor_x + dx) % self.inv.cols
        self.cursor_y = (self.cursor_y + dy) % self.inv.rows

    def draw_status(self, screen):

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            (self.left_x, self.y, self.panel_w, self.grid_height)
        )

        font = pygame.font.SysFont(None, 28)

        hp_text = font.render(f"HP: {self.player.health}", True, (255, 80, 80))
        def_text = font.render(f"DEF: {getattr(self.player, 'defense', 0)}", True, (200, 200, 200))

        screen.blit(hp_text, (self.left_x + 20, self.y + 30))
        screen.blit(def_text, (self.left_x + 20, self.y + 70))

    def draw_equipment(self, screen):

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            (self.right_x, self.y, self.panel_w, self.grid_height)
        )

        font = pygame.font.SysFont(None, 28)

        weapon = getattr(self.player, "weapon", None)
        armor = getattr(self.player, "armor", None)

        w_text = font.render("Weapon:", True, (255, 255, 255))
        a_text = font.render("Armor:", True, (255, 255, 255))

        screen.blit(w_text, (self.right_x + 20, self.y + 30))
        screen.blit(a_text, (self.right_x + 20, self.y + 120))

        if weapon:
            screen.blit(weapon.image, (self.right_x + 20, self.y + 60))

        if armor:
            screen.blit(armor.image, (self.right_x + 20, self.y + 150))

    def draw_grid(self, screen):

        pygame.draw.rect(
            screen,
            (20, 20, 20),
            (self.grid_x - 10, self.y - 10, self.grid_width + 20, self.grid_height + 20)
        )

        for y in range(self.inv.rows):
            for x in range(self.inv.cols):

                slot_x = self.grid_x + x * (self.slot_size + self.padding)
                slot_y = self.y + y * (self.slot_size + self.padding)

                pygame.draw.rect(
                    screen,
                    (80, 80, 80),
                    (slot_x, slot_y, self.slot_size, self.slot_size)
                )

                item = self.inv.grid[y][x]

                if item:
                    screen.blit(
                        item.image,
                        (
                            slot_x + (self.slot_size - item.image.get_width()) // 2,
                            slot_y + (self.slot_size - item.image.get_height()) // 2
                        )
                    )

                if x == self.cursor_x and y == self.cursor_y:
                    pygame.draw.rect(
                        screen,
                        (255, 215, 0),
                        (slot_x, slot_y, self.slot_size, self.slot_size),
                        3
                    )

    def draw(self, screen):
        self.draw_status(screen)
        self.draw_grid(screen)
        self.draw_equipment(screen)