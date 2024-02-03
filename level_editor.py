"""This is a level editor to create mario levels with different obstacles and tiles."""

import pygame
import pickle
from os import path
import csv


pygame.init()

clock = pygame.time.Clock()
fps = 60

# game window
lower_margin = 100
side_margin = 300
screen_width = 800
screen_height = 640

screen = pygame.display.set_mode(
    (screen_width + side_margin, screen_height + lower_margin)
)
pygame.display.set_caption("Level Editor")

# define game variables
rows = 16
max_cols = 150
tile_size = screen_height // rows
clicked = False
tile_types = 17
level = 1
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
current_tile = 0

img_list = []
# load images
bg_img1 = pygame.image.load("img/background.gif").convert_alpha()
bg_img1 = pygame.transform.scale(bg_img1, (screen_width, screen_height))
bg_img2 = pygame.image.load("img/background3.jpg").convert_alpha()
bg_img2 = pygame.transform.scale(bg_img2, (screen_width, screen_height))
for x in range(tile_types):
    if x >= 0 and x <= 5:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (tile_size, tile_size))
        img_list.append(img)
    if x >= 10 and x <= 13:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (tile_size, tile_size))
        img_list.append(img)
    if x == 6:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (tile_size * 2, tile_size))
        img_list.append(img)
    if x == 7:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (tile_size * 2, tile_size * 2))
        img_list.append(img)
    if x == 8:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (tile_size * 2, tile_size * 3))
        img_list.append(img)
    if x == 9:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (tile_size * 2, tile_size * 4))
        img_list.append(img)
    if x == 14:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (tile_size * 3, tile_size // 2))
        img_list.append(img)
    if x == 15:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (tile_size * 3, tile_size // 2))
        img_list.append(img)
    if x == 16:
        img = pygame.image.load(f"img/tile/{x}.png")
        img = pygame.transform.scale(img, (tile_size * 1.5, tile_size))
        img_list.append(img)


save_img = pygame.image.load("img/save_btn.png").convert_alpha()
load_img = pygame.image.load("img/load_btn.png").convert_alpha()


# define colours
white = (255, 255, 255)
green = (144, 201, 120)
red = (200, 25, 25)

font = pygame.font.SysFont("Futura", 24)

# create empty tile list
world_data = []
for row in range(rows):
    r = [-1] * max_cols
    world_data.append(r)

# create ground
for tile in range(0, max_cols):
    world_data[rows - 1][tile] = 0


# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(green)
    width1 = bg_img1.get_width()
    width2 = bg_img2.get_width()
    for x in range(8):
        if level == 1:
            screen.blit(bg_img1, ((x * width1) - scroll, 0))
        if level == 2:
            screen.blit(bg_img2, ((x * width2) - scroll, 0))


def draw_grid():
    # vertical lines
    for c in range(max_cols + 1):
        pygame.draw.line(
            screen,
            white,
            (c * tile_size - scroll, 0),
            (c * tile_size - scroll, screen_height),
        )
    # horizontal lines
    for c in range(rows + 1):
        pygame.draw.line(
            screen, white, (0, c * tile_size), (screen_width, c * tile_size)
        )


def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * tile_size - scroll, y * tile_size))


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


# create load and save buttons
save_button = Button(screen_width // 2 - 150, screen_height - 1, save_img)
load_button = Button(screen_width // 2 + 50, screen_height - 1, load_img)


# create buttons
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = Button(
        screen_width + (75 * button_col) + 50, 75 * button_row + 50, img_list[i]
    )
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0


# main game loop
run = True
while run:

    clock.tick(fps)

    draw_bg()
    draw_grid()
    draw_world()

    draw_text(f"Level: {level}", font, white, 10, screen_height + lower_margin - 90)
    draw_text(
        "Press UP or DOWN to change level",
        font,
        white,
        10,
        screen_height + lower_margin - 60,
    )

    # save and load data
    if save_button.draw():
        # save level data
        with open(f"level{level}_data.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            for row in world_data:
                writer.writerow(row)
    if load_button.draw():
        # load in level data
        # reset scroll back to the start of the level
        scroll = 0
        with open(f"level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)

    # draw tile panel and tiles
    pygame.draw.rect(screen, green, (screen_width, 0, side_margin, screen_height))

    # choose a tile
    button_count = 0
    for button_count, i in enumerate(button_list):
        if i.draw():
            current_tile = button_count

    # highlight the selected tile
    pygame.draw.rect(screen, red, button_list[current_tile].rect, 3)

    # scroll the map
    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True and scroll < (max_cols * tile_size) - screen_width:
        scroll += 5 * scroll_speed

    # add new tiles to the screen
    # get mouse position
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // tile_size
    y = pos[1] // tile_size

    # #check that the coordinates are within the tile area
    if pos[0] < screen_width and pos[1] < screen_height:
        # update tile value
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()
