import pygame
import copy


class StorageChestUI:

    def __init__(
            self,
            player_inventory,
            chest_inventory,
            screen_width=1280,
            screen_height=768
    ):

        self.player_inventory = player_inventory
        self.chest_inventory = chest_inventory

        self.slot_size = 64
        self.padding = 10

        self.player_cursor_x = 0
        self.player_cursor_y = 0

        self.chest_cursor_x = 0
        self.chest_cursor_y = 0

        self.focus = "player"

        self.open = False

        self.font = pygame.font.SysFont(None, 26)

        self.player_grid_width = (
                player_inventory.cols * self.slot_size
                + (player_inventory.cols - 1) * self.padding
        )

        self.chest_grid_width = (
                chest_inventory.cols * self.slot_size
                + (chest_inventory.cols - 1) * self.padding
        )

        self.player_grid_height = (
                player_inventory.rows * self.slot_size
                + (player_inventory.rows - 1) * self.padding
        )

        self.chest_grid_height = (
                chest_inventory.rows * self.slot_size
                + (chest_inventory.rows - 1) * self.padding
        )

        self.player_x = 60
        self.player_y = 150

        self.chest_x = 650
        self.chest_y = 80

    # ==========================================
    # CURSOR
    # ==========================================

    def move_cursor(self, dx, dy):

        if self.focus == "player":

            self.player_cursor_x = (
                    self.player_cursor_x + dx
            ) % self.player_inventory.cols

            self.player_cursor_y = (
                    self.player_cursor_y + dy
            ) % self.player_inventory.rows

        else:

            self.chest_cursor_x = (
                    self.chest_cursor_x + dx
            ) % self.chest_inventory.cols

            self.chest_cursor_y = (
                    self.chest_cursor_y + dy
            ) % self.chest_inventory.rows

    def switch_focus(self):

        if self.focus == "player":
            self.focus = "chest"
        else:
            self.focus = "player"

    # ==========================================
    # GET ITEM
    # ==========================================

    def get_selected_item(self):

        if self.focus == "player":

            return self.player_inventory.grid[
                self.player_cursor_y
            ][
                self.player_cursor_x
            ]

        return self.chest_inventory.grid[
            self.chest_cursor_y
        ][
            self.chest_cursor_x
        ]

    # ==========================================
    # TRANSFER
    # ==========================================

    def transfer_one(self):

        item = self.get_selected_item()

        if not item:
            return

        if self.focus == "player":

            if item.stackable:

                single = copy.copy(item)
                single.quantity = 1

                if self.chest_inventory.add_item(single):
                    self.player_inventory.remove_quantity(item, 1)

            else:

                if self.chest_inventory.add_item(item):
                    self.player_inventory.remove_item(item)

        else:

            if item.stackable:

                single = copy.copy(item)
                single.quantity = 1

                if self.player_inventory.add_item(single):
                    self.chest_inventory.remove_quantity(item, 1)

            else:

                if self.player_inventory.add_item(item):
                    self.chest_inventory.remove_item(item)

    def transfer_stack(self):

        item = self.get_selected_item()

        if not item:
            return

        if self.focus == "player":

            if self.chest_inventory.add_item(item):
                self.player_inventory.remove_item(item)

        else:

            if self.player_inventory.add_item(item):
                self.chest_inventory.remove_item(item)

    # ==========================================
    # DRAW GRID
    # ==========================================

    def draw_inventory(
            self,
            screen,
            inventory,
            start_x,
            start_y,
            cursor_x,
            cursor_y,
            active
    ):

        width = (
                inventory.cols * self.slot_size
                + (inventory.cols - 1) * self.padding
        )

        height = (
                inventory.rows * self.slot_size
                + (inventory.rows - 1) * self.padding
        )

        border_color = (
            (255, 215, 0)
            if active
            else
            (120, 120, 120)
        )

        pygame.draw.rect(
            screen,
            border_color,
            (
                start_x - 12,
                start_y - 12,
                width + 24,
                height + 24
            ),
            3
        )

        for y in range(inventory.rows):

            for x in range(inventory.cols):

                slot_x = start_x + x * (
                        self.slot_size + self.padding
                )

                slot_y = start_y + y * (
                        self.slot_size + self.padding
                )

                pygame.draw.rect(
                    screen,
                    (80, 80, 80),
                    (
                        slot_x,
                        slot_y,
                        self.slot_size,
                        self.slot_size
                    )
                )

                item = inventory.grid[y][x]

                if item and item.image:

                    screen.blit(
                        item.image,
                        (
                            slot_x +
                            (
                                    self.slot_size
                                    - item.image.get_width()
                            ) // 2,

                            slot_y +
                            (
                                    self.slot_size
                                    - item.image.get_height()
                            ) // 2
                        )
                    )

                if item and item.quantity > 1:

                    text = self.font.render(
                        str(item.quantity),
                        True,
                        (255, 255, 255)
                    )

                    screen.blit(
                        text,
                        (
                            slot_x + 40,
                            slot_y + 40
                        )
                    )

                if x == cursor_x and y == cursor_y:

                    pygame.draw.rect(
                        screen,
                        (255, 215, 0),
                        (
                            slot_x,
                            slot_y,
                            self.slot_size,
                            self.slot_size
                        ),
                        3
                    )

    # ==========================================
    # DRAW
    # ==========================================

    def draw(self, screen):

        overlay = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 180))

        screen.blit(overlay, (0, 0))

        title1 = self.font.render(
            "PLAYER INVENTORY",
            True,
            (255, 255, 255)
        )

        title2 = self.font.render(
            "STORAGE CHEST",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title1,
            (self.player_x, self.player_y - 40)
        )

        screen.blit(
            title2,
            (self.chest_x, self.chest_y - 40)
        )

        self.draw_inventory(
            screen,
            self.player_inventory,
            self.player_x,
            self.player_y,
            self.player_cursor_x,
            self.player_cursor_y,
            self.focus == "player"
        )

        self.draw_inventory(
            screen,
            self.chest_inventory,
            self.chest_x,
            self.chest_y,
            self.chest_cursor_x,
            self.chest_cursor_y,
            self.focus == "chest"
        )

        help_text = self.font.render(
            "TAB=Switch  T=Move One  Shift+T=Move Stack  ESC=Close",
            True,
            (255, 255, 0)
        )

        screen.blit(
            help_text,
            (250, 700)
        )