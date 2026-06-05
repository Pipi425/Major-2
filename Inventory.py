import pygame


# ================= ITEM SYSTEM =================
class Item:
    def __init__(self, name, image_path=None, description="", item_type="misc"):
        self.name = name
        self.description = description
        self.type = item_type
        self.sounds = [
            pygame.mixer.Sound("SoundEffects/Bite.mp3"),
            pygame.mixer.Sound("SoundEffects/Equip.mp3")
        ]
        self.sounds[1].set_volume(0.5)


        self.image = None
        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32))

    def use(self, player, inventory):
        print(f"{self.name} cannot be used.")


class Weapon(Item):
    def __init__(self, name, image_path, description, attack=0, cooldown=0):
        super().__init__(name, image_path, description, "weapon")
        self.attack = attack
        self.cooldown = cooldown

    def use(self, player, inventory):
        self.sounds[1].play()

        if getattr(player, "weapon", None):
            inventory.add_item(player.weapon)

        player.weapon = self
        inventory.remove_item(self)

class Bow(Item):
    def __init__(self, name, image_path, description,
                 damage=0, cooldown=0):
        super().__init__(name, image_path, description, "bow")

        self.damage = damage
        self.cooldown = cooldown

    def use(self, player, inventory):

        self.sounds[1].play()

        if getattr(player, "bow", None):
            inventory.add_item(player.bow)

        player.bow = self

        inventory.remove_item(self)


class Armor(Item):
    def __init__(self, name, image_path, description,
                 defense=0, slot="chest"):
        super().__init__(name, image_path, description, "armor")

        self.defense = defense
        self.slot = slot  # head, chest, hands, legs

    def use(self, player, inventory):
        self.sounds[1].play()

        old_max = player.max_health

        if self.slot == "head":

            if player.head_armor:
                inventory.add_item(player.head_armor)

            player.head_armor = self

        elif self.slot == "chest":

            if player.chest_armor:
                inventory.add_item(player.chest_armor)

            player.chest_armor = self

        elif self.slot == "hands":

            if player.hand_armor:
                inventory.add_item(player.hand_armor)

            player.hand_armor = self

        elif self.slot == "legs":

            if player.leg_armor:
                inventory.add_item(player.leg_armor)

            player.leg_armor = self

        new_max = player.max_health

        player.health += (new_max - old_max)

        if player.health > player.max_health:
            player.health = player.max_health

        inventory.remove_item(self)


class Consumable(Item):
    def __init__(self, name, image_path, description, heal=0):
        super().__init__(name, image_path, description, "consumable")
        self.heal = heal

    def use(self, player, inventory):
        self.sounds[0].play()

        if player.health + self.heal >= player.max_health:
            player.health = player.max_health
            inventory.remove_item(self)
        else:
            player.health += self.heal
            inventory.remove_item(self)


class Misc(Item):
    def __init__(self, name, image_path, description):
        super().__init__(name, image_path, description, "misc")

    def use(self, player, inventory):
        pass


# ================= INVENTORY =================
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
                    return True
        return False

    def clear(self):
        for y in range(self.rows):
            for x in range(self.cols):
                self.grid[y][x] = None


# ================= UI =================
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
        self.hover_pos = pygame.Rect(0, 0, 0, 0)
        self.hover_delay = 750
        self.font = pygame.font.SysFont(None, 22)

        self.weapon_rect = pygame.Rect(
            self.right_x + 20,
            self.y + 60,
            32,
            32
        )

        self.bow_rect = pygame.Rect(
            self.right_x + 120,
            self.y + 60,
            32,
            32
        )

        self.head_rect = pygame.Rect(
            self.right_x + 20,
            self.y + 150,
            32, 32
        )

        self.chest_rect = pygame.Rect(
            self.right_x + 20,
            self.y + 210,
            32, 32
        )

        self.hand_rect = pygame.Rect(
            self.right_x + 120,
            self.y + 150,
            32, 32
        )

        self.leg_rect = pygame.Rect(
            self.right_x + 120,
            self.y + 210,
            32, 32
        )

    # ================= CURSOR =================
    def move_cursor(self, dx, dy):
        self.cursor_x = (self.cursor_x + dx) % self.inv.cols
        self.cursor_y = (self.cursor_y + dy) % self.inv.rows

    def get_selected_item(self):
        return self.inv.grid[self.cursor_y][self.cursor_x]

    # ================= DRAW =================
    def draw_status(self, screen):

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            (self.left_x, self.y, self.panel_w, self.grid_height)
        )

        font = pygame.font.SysFont(None, 28)

        hp_text = font.render(
            f"HP: {self.player.health}/{self.player.max_health}",
            True,
            (255, 80, 80)
        )

        def_text = font.render(
            f"DEF: {getattr(self.player, 'defense', 0)}",
            True,
            (200, 200, 200)
        )

        screen.blit(hp_text, (self.left_x + 20, self.y + 30))
        screen.blit(def_text, (self.left_x + 20, self.y + 70))

        # ================= WEAPON =================

        weapon = getattr(self.player, "weapon", None)
        bow = getattr(self.player, "bow", None)

        screen.blit(
            font.render("Weapon", True, (255, 255, 255)),
            (self.left_x + 20, self.y + 130)
        )

        screen.blit(
            font.render("Bow", True, (255, 255, 255)),
            (self.left_x + 120, self.y + 130)
        )

        weapon_pos = (self.left_x + 20, self.y + 170)
        bow_pos = (self.left_x + 120, self.y + 170)

        self.weapon_rect.topleft = weapon_pos
        self.bow_rect.topleft = bow_pos

        if weapon and weapon.image:
            screen.blit(weapon.image, weapon_pos)

        if bow and bow.image:
            screen.blit(bow.image, bow_pos)

    def draw_equipment(self, screen):

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            (self.right_x, self.y, self.panel_w, self.grid_height)
        )

        font = pygame.font.SysFont(None, 28)

        head = getattr(self.player, "head_armor", None)
        chest = getattr(self.player, "chest_armor", None)
        hands = getattr(self.player, "hand_armor", None)
        legs = getattr(self.player, "leg_armor", None)

        # ===== 左列 =====

        screen.blit(
            font.render("Head", True, (255, 255, 255)),
            (self.right_x + 20, self.y + 30)
        )

        screen.blit(
            font.render("Chest", True, (255, 255, 255)),
            (self.right_x + 20, self.y + 140)
        )

        # ===== 右列 =====

        screen.blit(
            font.render("Hands", True, (255, 255, 255)),
            (self.right_x + 120, self.y + 30)
        )

        screen.blit(
            font.render("Legs", True, (255, 255, 255)),
            (self.right_x + 120, self.y + 140)
        )

        head_pos = (self.right_x + 20, self.y + 70)
        chest_pos = (self.right_x + 20, self.y + 180)

        hand_pos = (self.right_x + 120, self.y + 70)
        leg_pos = (self.right_x + 120, self.y + 180)

        self.head_rect.topleft = head_pos
        self.chest_rect.topleft = chest_pos

        self.hand_rect.topleft = hand_pos
        self.leg_rect.topleft = leg_pos

        if head and head.image:
            screen.blit(head.image, head_pos)

        if chest and chest.image:
            screen.blit(chest.image, chest_pos)

        if hands and hands.image:
            screen.blit(hands.image, hand_pos)

        if legs and legs.image:
            screen.blit(legs.image, leg_pos)

    def draw_grid(self, screen):
        pygame.draw.rect(screen, (20, 20, 20),
                         (self.grid_x - 10, self.y - 10,
                          self.grid_width + 20, self.grid_height + 20))

        for y in range(self.inv.rows):
            for x in range(self.inv.cols):

                slot_x = self.grid_x + x * (self.slot_size + self.padding)
                slot_y = self.y + y * (self.slot_size + self.padding)

                pygame.draw.rect(screen, (80, 80, 80),
                                 (slot_x, slot_y, self.slot_size, self.slot_size))

                item = self.inv.grid[y][x]

                if item and item.image:
                    screen.blit(item.image,
                                (slot_x + (self.slot_size - item.image.get_width()) // 2,
                                 slot_y + (self.slot_size - item.image.get_height()) // 2))

                if x == self.cursor_x and y == self.cursor_y:
                    pygame.draw.rect(screen, (255, 215, 0),
                                     (slot_x, slot_y, self.slot_size, self.slot_size), 3)

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

        if pygame.time.get_ticks() - self.hover_timer < self.hover_delay:
            return

        text = self.hover_item.description
        if not text:
            return

        render = self.font.render(text, True, (255, 255, 255))

        x = self.hover_pos.x
        y = self.hover_pos.y + 45

        bg = pygame.Rect(x, y, render.get_width() + 16, render.get_height() + 16)

        pygame.draw.rect(screen, (0, 0, 0), bg, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), bg, 1, border_radius=6)

        screen.blit(render, (x + 8, y + 8))

    # ================= MOUSE =================
    def get_item_under_mouse(self, mouse_pos):
        mx, my = mouse_pos

        for y in range(self.inv.rows):
            for x in range(self.inv.cols):

                slot_x = self.grid_x + x * (self.slot_size + self.padding)
                slot_y = self.y + y * (self.slot_size + self.padding)

                rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)

                if rect.collidepoint(mx, my):
                    return self.inv.grid[y][x], rect

        if self.weapon_rect.collidepoint(mx, my):
            return getattr(self.player, "weapon", None), self.weapon_rect

        if self.bow_rect.collidepoint(mx, my):
            return getattr(self.player, "bow", None), self.bow_rect

        if self.head_rect.collidepoint(mx, my):
            return self.player.head_armor, self.head_rect

        if self.chest_rect.collidepoint(mx, my):
            return self.player.chest_armor, self.chest_rect

        if self.hand_rect.collidepoint(mx, my):
            return self.player.hand_armor, self.hand_rect

        if self.leg_rect.collidepoint(mx, my):
            return self.player.leg_armor, self.leg_rect

        return None, None

    def update_hover(self, mouse_pos):
        item, rect = self.get_item_under_mouse(mouse_pos)

        now = pygame.time.get_ticks()

        if item:
            if item != self.hover_item:
                self.hover_item = item
                self.hover_timer = now
                self.hover_pos = rect
        else:
            self.hover_item = None
            self.hover_pos = pygame.Rect(0, 0, 0, 0)
            self.hover_timer = 0

    # ================= USE =================
    def handle_use(self, player, inventory):
        item = self.get_selected_item()
        if not item:
            return

        if not hasattr(item, "use"):
            return

        item.use(player, inventory)