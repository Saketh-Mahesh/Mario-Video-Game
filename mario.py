"""This is my recreation of an old school mario video game. This is still a work in progress and I plan to add many more features that real mario games have, such as more enemies, power ups, etc.
For the meantime, I have created 2 test levels just to showcase what I have done so far.
"""


import pygame
import os
import csv
import button
from pygame import mixer


mixer.init()
pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mario")

# set font
FONT_SCORE = pygame.font.SysFont("Neo Sans", 40)

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
SCROLL_THRESH = 800
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 17
level = 1
bg_scroll = 0
screen_scroll = 0
game_over = 0
start_game = False
coin_score = 0
score = 0


# define player action variables
moving_left = False
moving_right = False


# load in music and sounds
pygame.mixer.music.load("img/theme_song.wav")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 5000)

coin_sound = pygame.mixer.Sound("img/coin.wav")
coin_sound.set_volume(0.5)
jump_sound = pygame.mixer.Sound("img/mario_jump.wav")
jump_sound.set_volume(0.05)
game_over_sound = pygame.mixer.Sound("img/game_over.wav")
game_over_sound.set_volume(0.5)
goomba_stomp_sound = pygame.mixer.Sound("img/goomba_stomp.wav")
goomba_stomp_sound.set_volume(0.7)
# load in background image
bg_img1 = pygame.image.load("img/background.gif").convert_alpha()
bg_img2 = pygame.image.load("img/background2.png").convert_alpha()
# load other images
start_img = pygame.image.load("img/start_btn.png").convert_alpha()
exit_img = pygame.image.load("img/exit_btn.png").convert_alpha()
restart_img = pygame.image.load("img/restart_btn.png").convert_alpha()
# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    if x >= 0 and x <= 5:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)
    if x >= 10 and x <= 13:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)
    if x == 6:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (TILE_SIZE * 2, TILE_SIZE))
        img_list.append(img)
    if x == 7:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (TILE_SIZE * 2, TILE_SIZE * 2))
        img_list.append(img)
    if x == 8:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (TILE_SIZE * 2, TILE_SIZE * 3))
        img_list.append(img)
    if x == 9:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (TILE_SIZE * 2, TILE_SIZE * 4))
        img_list.append(img)
    if x == 14:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (TILE_SIZE * 3, TILE_SIZE // 2))
        img_list.append(img)
    if x == 15:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)
    if x == 16:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (TILE_SIZE * 1.5, TILE_SIZE))
        img_list.append(img)
    # if x == 17:
    #     img = pygame.image.load(f"img/tile/{x}.png")
    #     img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    #     img_list.append(img)

# define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# define font
font = pygame.font.SysFont("Futura", 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width1 = bg_img1.get_width()
    width2 = bg_img2.get_width()
    for x in range(8):
        if level == 1:
            screen.blit(bg_img1, ((x * width1) - bg_scroll * 0.5, 0))
        if level == 2:
            screen.blit(bg_img2, ((x * width2) - bg_scroll * 0.5, 0))


def reset_level():
    goomba_group.empty()
    question_box_group.empty()
    coin_group.empty()
    exit_group.empty()
    platform_group.empty()
    spike_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


# Version 2 of Player Class:
class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the players
        animation_types = ["Idle", "Run", "Jump"]
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f"img/{self.char_type}/{animation}"))
            for i in range(num_of_frames):
                img = pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png")
                img = pygame.transform.scale(
                    img, (int(img.get_width() * scale), int(img.get_height() * scale))
                )
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0
        collision_thresh = 20

        if self.alive == True:
            # assign movement variables if moving left or right
            if moving_left:
                dx = -self.speed
                self.flip = True
                self.direction = -1
            if moving_right:
                dx = self.speed
                self.flip = False
                self.direction = 1

            # jump
            if self.jump == True and self.in_air == False:
                self.vel_y = -11
                self.jump = False
                self.in_air = True

            # apply gravity
            self.vel_y += GRAVITY
            if self.vel_y > 10:
                self.vel_y
            dy += self.vel_y

            ###COLLISION STUFF###

            # check for collision with obstacle tiles
            for tile in world.obstacle_list:
                # check collision in the x direction
                if tile[1].colliderect(
                    self.rect.x + dx, self.rect.y, self.width, self.height
                ):
                    dx = 0
                # check for collision in the y direction
                if tile[1].colliderect(
                    self.rect.x, self.rect.y + dy, self.width, self.height
                ):
                    # check if below the ground, i.e. jumping
                    if self.vel_y < 0:
                        self.vel_y = 0
                        dy = tile[1].bottom - self.rect.top
                    # check if above the ground, i.e. falling
                    elif self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = tile[1].top - self.rect.bottom

            # check for collision with goomba enemies
            if pygame.sprite.spritecollide(self, goomba_group, False):
                self.alive = False

            # check for collision with spike
            if pygame.sprite.spritecollide(self, spike_group, False):
                self.alive = False

            # check for collision with exit
            level_complete = False
            if pygame.sprite.spritecollide(self, exit_group, False):
                level_complete = True

            # check for collision with question box
            global coin_score
            for question_box in question_box_group:
                if question_box.rect.colliderect(
                    self.rect.x + dx, self.rect.y, self.width, self.height
                ):
                    dx = 0
                if question_box.rect.colliderect(
                    self.rect.x, self.rect.y + dy, self.width, self.height
                ):
                    if (
                        abs((self.rect.top + dy) - question_box.rect.bottom)
                        < collision_thresh
                    ):
                        self.vel_y = 0
                        dy = question_box.rect.bottom - self.rect.top
                        question_box.image = pygame.image.load(
                            "img/question_block2.png"
                        )
                        question_box.image = pygame.transform.scale(
                            question_box.image, (TILE_SIZE, TILE_SIZE)
                        )
                        coin_sound.play()
                        coin_score += 1

                    elif (
                        abs((self.rect.bottom + dy) - question_box.rect.top)
                        < collision_thresh
                    ):
                        self.rect.bottom = question_box.rect.top
                        self.vel_y = 0
                        self.in_air = False
                        dy = 0

            # check for collision with moving platforms
            for platform in platform_group:
                if platform.rect.colliderect(
                    self.rect.x + dx, self.rect.y, self.width, self.height
                ):
                    dx = 0
                if platform.rect.colliderect(
                    self.rect.x, self.rect.y + dy, self.width, self.height
                ):
                    if (
                        abs((self.rect.top + dy) - platform.rect.bottom)
                        < collision_thresh
                    ):
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top

                    elif (
                        abs((self.rect.bottom + dy) - platform.rect.top)
                        < collision_thresh
                    ):
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                        self.vel_y = 0

            # update rectangle position
            self.rect.x += dx
            self.rect.y += dy

            # update scroll based on player position
            if self.char_type == "player":
                if (
                    self.rect.right > SCREEN_WIDTH - SCROLL_THRESH
                    and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH
                ) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                    self.rect.x -= dx
                    if self.alive == True:
                        screen_scroll = -dx

            # check if player has gone off screen
            if self.rect.top > SCREEN_HEIGHT:
                self.alive = False

            # check if player has died
        # elif self.alive == False:
        #     self.image = pygame.image.load('img/death.png')
        #     self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        #     if self.rect.y > 200:
        #         self.rect.y -= 5

        return screen_scroll, level_complete

    def update_animation(self):
        if self.alive == True:
            # update animation
            ANIMATION_COOLDOWN = 100
            # update image depending on current frame
            self.image = self.animation_list[self.action][self.frame_index]
            # check if enough time has passed since the last update
            if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
            # if the animation has run out the reset back to the start
            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0

    def update_action(self, new_action):
        if self.alive == True:
            # check if the new action is different to the previous one
            if new_action != self.action:
                self.action = new_action
                # update the animation settings
                self.frame_index = 0
                self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)

                    if tile >= 0 and tile <= 2:
                        self.obstacle_list.append(tile_data)
                    if tile == 3:
                        question_box = QuestionBox(x * TILE_SIZE, y * TILE_SIZE)
                        question_box_group.add(question_box)
                    elif tile == 4 or tile == 13:
                        goomba = Goomba(x * TILE_SIZE, y * TILE_SIZE)
                        goomba_group.add(goomba)
                    elif tile == 5:
                        coin = Coin(x * TILE_SIZE, y * TILE_SIZE)
                        coin_group.add(coin)
                    elif tile >= 6 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile == 9:
                        exit = Exit(x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
                    elif tile >= 10 and tile <= 12:
                        self.obstacle_list.append(tile_data)
                    elif tile == 14:
                        platform = Platform(x * TILE_SIZE, y * TILE_SIZE, 0, 1)
                        platform_group.add(platform)
                    elif tile == 15:
                        platform = Platform(x * TILE_SIZE, y * TILE_SIZE, 1, 0)
                        platform_group.add(platform)
                    elif tile == 16:
                        spike = Spike(x * TILE_SIZE, y * TILE_SIZE)
                        spike_group.add(spike)

        return player

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Goomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        if level == 1:
            self.image = pygame.image.load("img/goomba0.png")
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        if level == 2:
            self.image = pygame.image.load("img/blue_goomba.png")
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.enemy_image = []
        self.index = 0
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        overlap_tolerance = 15
        global score
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
        self.rect.x += screen_scroll

        if player.rect.colliderect(self.rect):
            if player.rect.bottom - self.rect.top < overlap_tolerance:
                goomba_stomp_sound.play()
                self.image = pygame.image.load("img/goomba2.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

                self.kill()
                score += 200

        else:
            player.kill()


class QuestionBox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/question_block.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x += screen_scroll


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/coin.png").convert_alpha()
        self.image = pygame.transform.scale(
            self.image, (TILE_SIZE // 2, TILE_SIZE // 2)
        )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/exit.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 4))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x += screen_scroll


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spike.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 1.5, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x += screen_scroll


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/platform.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 3, TILE_SIZE // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.rect.x += screen_scroll
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


# create buttons
start_button = button.Button(
    SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1
)
exit_button = button.Button(
    SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1
)
restart_button = button.Button(
    SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2
)

player = Player("player", 200, 200, 0.3, 5)
# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# load in level data and create world
with open(f"level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

# creating sprite groups
goomba_group = pygame.sprite.Group()
question_box_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()


world = World()
player = world.process_data(world_data)


# main game loop

run = True
while run:

    clock.tick(FPS)
    if start_game == False:
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False

    else:

        draw_bg()
        world.draw()

        player.update_animation()
        player.draw()

        question_box_group.update()
        question_box_group.draw(screen)

        coin_group.update()
        coin_group.draw(screen)

        exit_group.update()
        exit_group.draw(screen)

        platform_group.update()
        platform_group.draw(screen)

        spike_group.update()
        spike_group.draw(screen)

        # goomba.draw()
        if player.alive == True:
            goomba_group.update()

            # check if a coin has been collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                coin_sound.play()
                coin_score += 1
            coin_img = pygame.image.load("img/coin.png")
            screen.blit(coin_img, (TILE_SIZE // 2, TILE_SIZE // 2))

            draw_text("x " + str(coin_score), FONT_SCORE, WHITE, TILE_SIZE - 6, 10)
            draw_text("MARIO", FONT_SCORE, WHITE, TILE_SIZE + 70, 10)
            draw_text(str(score), FONT_SCORE, WHITE, TILE_SIZE + 70, 40)

        goomba_group.draw(screen)

        # update player actions
        if player.alive == True:

            if player.in_air:
                player.update_action(2)  # 2: jump
            elif moving_left or moving_right:
                player.update_action(1)  # 1: run
            else:
                player.update_action(0)  # 0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            if level_complete:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                score = 0
                player.alive = True
                with open(f"level{level}_data.csv", newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter=",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player = world.process_data(world_data)

        else:
            # game_over_sound.play()
            player.image = pygame.image.load("img/death.png")
            player.image = pygame.transform.scale(player.image, (50, 50))
            if player.rect.y > 500:
                player.rect.y += 5
            screen_scroll = 0
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()
                score = 0
                coin_score = 0
                player.alive = True
                with open(f"level{level}_data.csv", newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter=",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player = world.process_data(world_data)
                player = Player("player", 200, 200, 0.3, 5)

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False

        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
                jump_sound.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

    pygame.display.update()

pygame.quit()
