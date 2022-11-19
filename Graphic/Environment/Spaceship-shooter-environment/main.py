import pygame
import os
import time
import random
from spritesheet import SpriteSheet
pygame.font.init()

WIDTH = 600
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Cosmic war')

ENEMY_SMALL = pygame.image.load(os.path.join("spritesheets", "small1.png"))
sprite_sheet = SpriteSheet(ENEMY_SMALL)

ENEMY_MEDIUM = pygame.image.load(os.path.join("Graphic/Environment/Spaceplayer-shooter-environment/spritesheets", "medium1.png"))
sprite_sheet = SpriteSheet(ENEMY_MEDIUM)

ENEMY_BIG = pygame.image.load(os.path.join("Graphic/Environment/Spaceplayer-shooter-environment/spritesheets", "big1.png"))
sprite_sheet = SpriteSheet(ENEMY_BIG)

PLAYER_SHIP = pygame.image.load(os.path.join("Graphic/Environment/Spaceplayer-shooter-environment/spritesheets", "ship1.png"))
sprite_sheet = SpriteSheet(PLAYER_SHIP)

LASER_ENEMY = pygame.image.load(os.path.join("Graphic/Environment/Spaceplayer-shooter-environment/spritesheets", "laser-enemy1.png"))
LASER_PLAYER = pygame.image.load(os.path.join("Graphic/Environment/Spaceplayer-shooter-environment/spritesheets", "laser-player1.png"))

BG = pygame.transform.scale(pygame.image.load(os.path.join("Graphic/Environment/Spaceplayer-shooter-environment/backgrounds", "space.png")), (WIDTH, HEIGHT))



class Ship:
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.player_img = None
        self.laser_img = None
        self.laser = [ ]
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.player_img, (self.x, self.y))


class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.player_img = PLAYER_SHIP
        self.laser_img = LASER_PLAYER
        self.mask = pygame.mask.from_surface(self.player_img)
        self.max_health = health


def main():
    run = True
    FPS = 60
    level = 1
    lives = 4
    main_font = pygame.font.SysFont("comicsans", 50)
    player_vel = 5

    player = Player(300, 600)

    clock = pygame.time.Clock()

    def redraw_window():
        screen.blit(BG, (0, 0))

        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        screen.blit(lives_label, (10, 10))
        screen.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        
        player.draw(screen)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + 50 < WIDTH:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + 50 < HEIGHT:
            player.y += player_vel
            
main()