import pygame

class Enemy:
    def __init__(self, x, y):
        self.images = []

        for i in range(1, 7):
            img = pygame.image.load(f"fly_{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (60, 60))
            self.images.append(img)

        self.x = x
        self.y = y
        self.frame = 0
        self.count = 0
        self.speed = 1
        self.hp = 5
        self.alive = True
        self.stop = 0

    def get_image(self):
        return self.images[self.frame]

    def get_rect(self):
        return pygame.Rect(self.x + 8, self.y + 10, 30, 30)

    def get_center(self):
        image = self.get_image()
        rect = image.get_rect(topleft = (self.x, self.y))
        return rect.center

    def check_move(self, dx, dy, walls):
        test_rect = self.get_rect()
        test_rect = test_rect.move(dx, dy)

        for wall in walls:
            if test_rect.colliderect(wall):
                return False

        return True

    def move(self, player, walls):
        if self.stop > 0:
            self.stop -= 1
            return
        moving = False

        player_x, player_y = player.get_center()
        enemy_x, enemy_y = self.get_center()

        dx = 0
        dy = 0

        if player_x > enemy_x:
            dx = self.speed
        elif player_x < enemy_x:
            dx = -self.speed

        if player_y > enemy_y:
            dy = self.speed
        elif player_y < enemy_y:
            dy = -self.speed


        if self.check_move(dx, 0, walls):
            self.x += dx
            moving = True


        if self.check_move(0, dy, walls):
            self.y += dy
            moving = True

        if moving:
            self.count += 1
            if self.count >= 8:
                self.count = 0
                self.frame += 1

                if self.frame >= 6:
                    self.frame = 0

    def hit(self):
        self.hp -= 1
        self.stop = 20

        if self.hp <= 0:
            self.alive = False

    def draw(self, screen):
        if self.alive:
            screen.blit(self.get_image(), (self.x, self.y))