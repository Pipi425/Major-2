import pygame


class Item:
    def __init__(self, name, image_path=None, description="", item_type=None):
        self.name = name
        self.description = description
        self.type = item_type

        self.image = None
        if image_path:
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

    def remove_item(self, item):
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y][x] == item:
                    self.grid[y][x] = None
                    return


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

        self.hover_timer = 0
        self.hover_item = None
        self.hover_pos = (0, 0)
        self.hover_delay = 750
        self.font = pygame.font.SysFont(None, 22)

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

        if weapon and weapon.image:
            screen.blit(weapon.image, (self.right_x + 20, self.y + 60))

        if armor and armor.image:
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

                if item and item.image:
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

    def update_hover(self, mouse_pos):
        item, rect = self.get_item_under_mouse(mouse_pos)

        current_time = pygame.time.get_ticks()

        if item:
            if self.hover_item != item:
                self.hover_item = item
                self.hover_timer = current_time
                self.hover_pos = rect
        else:
            self.hover_item = None

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()

        self.update_hover(mouse_pos)

        self.draw_status(screen)
        self.draw_grid(screen)
        self.draw_equipment(screen)
        self.draw_tooltip(screen)

    def draw_tooltip(self, screen):
        if not self.hover_item:
            return

        current_time = pygame.time.get_ticks()

        if current_time - self.hover_timer < self.hover_delay:
            return

        text = self.hover_item.description
        if not text:
            return

        font = self.font
        render = font.render(text, True, (255, 255, 255))

        padding = 8

        x = self.hover_pos.x
        y = self.hover_pos.y + 45

        bg_rect = pygame.Rect(
            x,
            y,
            render.get_width() + padding * 2,
            render.get_height() + padding * 2
        )

        pygame.draw.rect(screen, (0, 0, 0), bg_rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, 1, border_radius=6)

        screen.blit(render, (x + padding, y + padding))

    def get_item_under_mouse(self, mouse_pos):
        mx, my = mouse_pos

        for y in range(self.inv.rows):
            for x in range(self.inv.cols):

                slot_x = self.grid_x + x * (self.slot_size + self.padding)
                slot_y = self.y + y * (self.slot_size + self.padding)

                rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)

                if rect.collidepoint(mx, my):
                    return self.inv.grid[y][x], rect

        weapon = getattr(self.player, "weapon", None)
        armor = getattr(self.player, "armor", None)

        weapon_rect = pygame.Rect(self.right_x + 20, self.y + 60, 32, 32)
        armor_rect = pygame.Rect(self.right_x + 20, self.y + 150, 32, 32)

        if weapon_rect.collidepoint(mx, my):
            return weapon, weapon_rect

        if armor_rect.collidepoint(mx, my):
            return armor, armor_rect

        return None, None

    def handle_click(self, mouse_pos):
        if not self.open:
            return

        item, rect = self.get_item_under_mouse(mouse_pos)
        if not item:
            return

        if item.type == "weapon":
            self.player.weapon = item

        elif item.type == "armor":
            self.player.armor = item