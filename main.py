import pygame
import sys
import os
import time
import random

from pygame import mixer
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

pygame.mixer.music.load("Audio/spaceshoot.mp3")
pygame.mixer.music.play(-1, 0.0, 5000)
pygame.mixer.music.set_volume(0.06)

laser_fx = pygame.mixer.Sound("Audio/Laser_Shoot2.wav")
laser_fx.set_volume(0.01)

getstar_fx = pygame.mixer.Sound("Audio/get_star.wav")
getstar_fx.set_volume(0.3)

#get heal and lives
getHL_fx = pygame.mixer.Sound("Audio/get_HL.wav")
getHL_fx.set_volume(0.1)

#get rapid and waterway
getRW_fx = pygame.mixer.Sound("Audio/get_RW.wav")
getRW_fx.set_volume(0.1)

import json
from operator import itemgetter
pygame.font.init()

WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
pygame.display.set_caption("Cosmic war")

ENEMY_SMALL = pygame.transform.scale(
    pygame.image.load("spritesheets/small1.png"), (20, 30))
ENEMY_MEDIUM = pygame.transform.scale(
    pygame.image.load("spritesheets/medium1.png"), (50, 32))
ENEMY_BIG = pygame.transform.scale(
    pygame.image.load("spritesheets/big1.png"), (70, 80))


PLAYER_SHIP = pygame.image.load(os.path.join("spritesheets", "ship1.png"))
PLAYER_SHIP1 = pygame.transform.scale(
    PLAYER_SHIP, (PLAYER_SHIP.get_width() * 2.5, PLAYER_SHIP.get_height() * 2.5))


LASER_PLAYER = pygame.transform.scale(
    pygame.image.load("spritesheets/laser-player1.png"), (20, 25))

LASER_ENEMY1 = pygame.transform.scale(pygame.image.load("spritesheets/laser-enemy.png"), (5, 10))
LASER_ENEMY2 = pygame.transform.scale(
    pygame.image.load("spritesheets/laser-enemy.png"), (10, 15))
LASER_ENEMY3 = pygame.transform.scale(
    pygame.image.load("spritesheets/laser-enemy.png"), (20, 25))

BG = pygame.transform.scale(pygame.image.load(
    os.path.join("backgrounds", "space.png")), (WIDTH, HEIGHT))

HEAL = pygame.transform.scale(
    pygame.image.load("itch/pngs/heal.png"), (30, 30))

RAPID = pygame.transform.scale(
    pygame.image.load("itch/Hex/slice37.png"), (30, 30))

WATERWAY = pygame.transform.scale(
    pygame.image.load("itch/PNG/1.png"), (30, 30))

LIVE_UP = pygame.transform.scale(
    pygame.image.load("itch/pngs/lives.png"), (30, 30))

STAR = pygame.transform.scale(
    pygame.image.load("itch/pngs/star.png"), (30, 30))

player_score = 0


playername = ' '
startDel = 0
isCooldown = 0


class Laser:
    def __init__(self, x, y, img, size):
        self.x = x + size
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)



class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        self.firerate = 1
        self.rapid_duration = 3000
        self.rapid_timer = 0
        self.start_rapid_timer = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
        if self.firerate != 1:
            self.rapid_timer = pygame.time.get_ticks()
            if self.rapid_timer - self.start_rapid_timer >= self.rapid_duration:
                self.firerate = 1
                self.rapid_timer = 0
                
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img, self.ship_img.get_width(
            )//2 - self.laser_img.get_width()//2)
            self.lasers.append(laser)
            self.cool_down_counter = 10 * self.firerate

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP1
        self.laser_img = LASER_PLAYER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

        self.Playerscore = 0

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if obj.__class__.__name__ == 'Enemy':
                            self.Playerscore += obj.value

                            if laser in self.lasers:
                                self.lasers.remove(laser)

                            pass
                            break

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y +
                         self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() +
                         10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    ENEMY_SIZE = {
        "small": (ENEMY_SMALL, LASER_ENEMY1),
        "medium": (ENEMY_MEDIUM, LASER_ENEMY2),
        "big": (ENEMY_BIG, LASER_ENEMY3)
    }

    def __init__(self, x, y, size, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.ENEMY_SIZE[size]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.value = 0
        if size == 'small':
            self.value = 10
        elif size == 'medium':
            self.value = 20
        elif size == 'big':
            self.value = 30

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img, self.ship_img.get_width(
            )//2 - self.laser_img.get_width()//2)
            self.lasers.append(laser)
            self.cool_down_counter = 0.5

class Heal:
    ITEM_MAP = {
        "heal": HEAL,
    }

    def __init__(self, x, y, item="heal"):
        self.x = x
        self.y = y
        self.ship_img = self.ITEM_MAP[item]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.vel = 1

    def draw(self, window):
        self.move()
        window.blit(self.ship_img, (self.x, self.y))

    def move(self):
        self.y += self.vel

    def collision(self, player):
        return collide(self, player)


class Rapid:
    ITEM_MAP = {
        "rapid": RAPID,
    }

    def __init__(self, x, y, item="rapid"):
        self.x = x
        self.y = y
        self.ship_img = self.ITEM_MAP[item]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.vel = 1

    def draw(self, window):
        self.move()
        window.blit(self.ship_img, (self.x, self.y))

    def move(self):
        self.y += self.vel

    def collision(self, player):
        return collide(self, player)


class Waterway:
    ITEM_MAP = {
        "waterway": WATERWAY,
    }

    def __init__(self, x, y, item="waterway"):
        self.x = x
        self.y = y
        self.ship_img = self.ITEM_MAP[item]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.vel = 1

    def draw(self, window):
        self.move()
        window.blit(self.ship_img, (self.x, self.y))

    def move(self):
        self.y += self.vel

    def collision(self, player):
        return collide(self, player)


class LiveUp:

    ITEM_MAP = {
        "live_Up": LIVE_UP,
    }

    def __init__(self, x, y, item="live_Up"):

        self.x = x
        self.y = y
        self.ship_img = self.ITEM_MAP[item]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.vel = 1

    def draw(self, window):
        self.move()
        window.blit(self.ship_img, (self.x, self.y))

    def move(self):
        self.y += self.vel

    def collision(self, player):
        return collide(self, player)


class Star:

    ITEM_MAP = {
        "star": STAR,
    }

    def __init__(self, x, y, item="star"):

        self.x = x
        self.y = y
        self.ship_img = self.ITEM_MAP[item]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.vel = 1

    def draw(self, window):
        self.move()
        window.blit(self.ship_img, (self.x, self.y))

    def move(self):
        self.y += self.vel

    def collision(self, player):
        return collide(self, player)


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(
                self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(
                self.text_input, True, self.base_color)


def get_font(size):
    return pygame.font.SysFont("leelawadeeuisemilight", size)

main_font = pygame.font.SysFont("leelawadeeuisemilight", 50)
lost_font = pygame.font.SysFont("leelawadeeuisemilight", 60)

def main():
    run = True

    pygame.mixer.music.play

    level = 0
    lives = 5

    

    enemies = []

    heals = []
    rapids = []
    waterways = []
    liveUp = []
    stars = []

    wave_length = 5
    enemy_vel = 1
    
    player_vel = 5
    laser_vel = 5

    player = Player(300, 600)
    global player_score
    player_score = 0
    player.Playerscore = player_score
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        screen.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score: {player.Playerscore}", 1, (255, 255, 255))

        screen.blit(lives_label, (WIDTH - level_label.get_width() - 10, 10))
        screen.blit(level_label, (WIDTH - level_label.get_width() - 10, 60))
        screen.blit(score_label, (10, 10))

        for enemy in enemies:
            enemy.draw(screen)

        for Heal in heals:
            Heal.draw(screen)

        for Rapid in rapids:
            Rapid.draw(screen)

        for Waterway in waterways:
            Waterway.draw(screen)

        for LiveUp in liveUp:
            LiveUp.draw(screen)

        for Star in stars:
            Star.draw(screen)

        player.draw(screen)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            screen.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        timepass = clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            player_score = player.Playerscore
            scoreName()
            updatescore()

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["small", "medium", "big"]))
                enemies.append(enemy)

            heal = Heal(random.randrange(0, WIDTH - 50),random.randrange(-800, -50))
            heals.append(heal)

            rapid = Rapid(random.randrange(0, WIDTH - 50),random.randrange(-800, -50))
            rapids.append(rapid)
            player.cool_down_counter = 10

            waterway = Waterway(random.randrange(0, WIDTH - 50), random.randrange(-800, -50))
            waterways.append(waterway)

            live_Up = LiveUp(random.randrange(0, WIDTH - 50),random.randrange(-800, -50))
            liveUp.append(live_Up)

            star = Star(random.randrange(0, WIDTH - 50),random.randrange(-800, -50))
            stars.append(star)
            get_star = False
            

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            laser_fx.play()
        if keys[pygame.K_ESCAPE]:
            run = False
            sys.exit

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                if get_star == False:
                    player.health -= 10
                else:
                    player.health += 0
                    player.Playerscore += enemy.value
                
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

        for heal in heals:
            if collide(heal, player):
                getHL_fx.play()
                if player.health <= 50:
                    player.health += 50
                    heals.remove(heal)
                elif player.health < 100:
                    player.health = 100
                    heals.remove(heal)
                elif player.health == 100:
                    player.health += 0
                    heals.remove(heal)

        for rapid in rapids:
            if collide(rapid, player):
                getRW_fx.play()
                player.firerate = 2.5
                player.start_rapid_timer = pygame.time.get_ticks()
                rapids.remove(rapid)

        for waterway in waterways:
            if collide(waterway, player):
                getRW_fx.play()
                player.firerate = 3
                player.start_rapid_timer = pygame.time.get_ticks()
                waterways.remove(waterway)

        for live_Up in liveUp:
            if collide(live_Up, player):
                getHL_fx.play()
                lives += 1
                liveUp.remove(live_Up)

        for star in stars:
            if collide(star, player):
                getstar_fx.play()
                stars.remove(star)
                get_star = True
                startime = 0
                starcooldown = 0
                currenttime = 0

        if get_star == True:
            
            currenttime += timepass
            startime = currenttime - starcooldown
            if startime > 5000:
                get_star = False
                currenttime = 0
                startime = 0
                starcooldown = 0

def scoreName():
    global player_score
    global playername
    global startDel
    global isCooldown
    
    #Gameover_fx.play()
    while True:
        screen.blit(BG, (0, 0))
        
        GameOver = get_font(60).render("Game Over", True, "White")
        screen.blit(GameOver, (130,100))

        EnterName = get_font(40).render("Please Enter your name", True, "White")
        screen.blit(EnterName, (80,200))

        PLAYERSCORE = main_font.render(f"PlayerScore:{playername,player_score}", 1, (255,255,255))
        screen.blit(PLAYERSCORE, (80, 300))

        NAME_TEXT = get_font(25).render("Paramate Jiembanjong 65010594", True, "Orange")
        NAME_RECT = NAME_TEXT.get_rect(center=(400, 670))
        screen.blit(NAME_TEXT, NAME_RECT)

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if playername.replace(" ","") == "":
                        playername = "Unknown"
                    
                    with open('score.json', 'r') as file:     #read
                        playerScore = json.load(file)

                    playerScore.append([playername,int(player_score)])
                    playerScore = sorted(playerScore,reverse= True, key=itemgetter(1))
                    if len(playerScore) > 5:
                        playerScore.pop()                     #take out

                    with open('score.json', 'w+') as file:
                        json.dump(playerScore, file)            
                    return
                elif not event.key == pygame.K_BACKSPACE:
                    playername += event.unicode
                    
        if pygame.key.get_pressed()[pygame.K_BACKSPACE] and not isCooldown:
            isCooldown = True
            startDel = pygame.time.get_ticks()         #start time counter
            if len(playername) <= 1:
                playername = ""
            else:
                playername = playername[:-1]        #Remove last character

        if len(playername) > 15:        #playername length
            playername = playername[:15]

        if (pygame.time.get_ticks() - startDel)/1000 >= 0.3 and isCooldown:
            isCooldown = False

        pygame.display.update()

#UpdateScore    
def updatescore():
    while True:
        UPDATESCORE_MOUSE_POS = pygame.mouse.get_pos()

        screen.blit(BG, (0, 0))

        UPDATESCORE_TEXT = get_font(70).render("Leaderboard", True, "#FFD700")
        UPDATESCORE_RECT = UPDATESCORE_TEXT.get_rect(center = (300, 100))
        screen.blit(UPDATESCORE_TEXT, UPDATESCORE_RECT)

        #read file
        with open('score.json', 'r') as file:            
            playerScore = json.load(file)

        for i,score in enumerate(playerScore):
        
        #Name
            NAME_TEXT = get_font(45).render(score[0], True, (255,255,255))
            screen.blit(NAME_TEXT, (100,150+ i*50))

        #Score
            SCORE_TEXT = get_font(45).render(str(score[1]), True, (255,255,255))
            screen.blit(SCORE_TEXT, (400,150+ i*50))

        UPDATESCORE_BACK = Button(image = None, pos = (300, 600), 
                            text_input = "BACK", font = get_font(75), base_color = (255,255,255), hovering_color = "#FFD700")

        UPDATESCORE_BACK.changeColor(UPDATESCORE_MOUSE_POS)
        UPDATESCORE_BACK.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if UPDATESCORE_BACK.checkForInput(UPDATESCORE_MOUSE_POS):
                    #MouseClick_fx.play()
                    main_menu()
                    

        pygame.display.update()


def main_menu():
    while True:
        screen.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(65).render("Cosmic War", True, "#FFD700")
        MENU_RECT = MENU_TEXT.get_rect(center=(300, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("itch/Play_Rect.png"), pos=(300, 250),
                             text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color = (255,255,255))
        SCORE_BUTTON = Button(image=pygame.image.load("itch/Play_Rect.png"), pos=(300, 400),
                              text_input="SCORE", font=get_font(75), base_color="#d7fcd4", hovering_color = (255,255,255))
        QUIT_BUTTON = Button(image=pygame.image.load("itch/Play_Rect.png"), pos=(300, 550),
                             text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color = (255,255,255))

        screen.blit(MENU_TEXT, MENU_RECT)

        NAME_TEXT = get_font(25).render("Paramate Jiembanjong 65010594", True, "Orange")
        NAME_RECT = NAME_TEXT.get_rect(center=(400, 670))

        screen.blit(NAME_TEXT, NAME_RECT)

        for button in [PLAY_BUTTON, SCORE_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    main()
                if SCORE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    updatescore()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
    
main_menu()
