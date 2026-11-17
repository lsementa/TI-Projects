import ti_draw
import random
import ti_graphics
from ti_system import *

# Dimensions
SCREEN_WIDTH  = 321
SCREEN_HEIGHT = 211
BUTTON_HEIGHT = 22
CHAR_W = 10

SPRITE_SIZE = 25

# Colors
BG_COLOR   = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)

# Keys
CLEAR_KEY = 45

# Grid of 25 x 25 cells, centered in the area above the footer
COLS     = SCREEN_WIDTH // SPRITE_SIZE                    # 12
ROWS     = (SCREEN_HEIGHT - BUTTON_HEIGHT) // SPRITE_SIZE # 7
GRID_X   = (SCREEN_WIDTH - COLS * SPRITE_SIZE) // 2
GRID_Y   = (SCREEN_HEIGHT - BUTTON_HEIGHT - ROWS * SPRITE_SIZE) // 2

# club.png: 25 x 25
club_palette = [2301728]
club_sprites = {0: [0, 402785299, 335808274, 302385425, 268962566, 638320899, 605290765, 202772489, 135795720, 102372871, 68949766, 840958210, 103287041, 438831873, 136972033, 438960645, 539625217, 204210945, 405537540, 640418305, 506331395, 372245762, 338822913]}

# diamond.png: 25 x 25
diamond_palette = [16646144]
diamond_sprites = {0: [0, 436470040, 403047189, 369624339, 336332559, 302909709, 269486859, 236195079, 202772229, 169349379, 135926529]}

# heart.png: 25 x 25
heart_palette = [16646144]
heart_sprites = {0: [0, 168166925, 537265933, 134744075, 503843082, 101321225, 470419977, 67901190, 437783553, 437914369, 404491010, 371067905, 203427841, 237112833, 270797825, 304482817, 338167809, 371852801, 405537538, 439353601]}

# spade.png: 25 x 25
spade_palette = [2301728]
spade_sprites = {0: [0, 436470296, 403047185, 369624336, 336201487, 302778638, 269355789, 235932940, 202510091, 169087242, 135664393, 102241544, 807141637, 69080835, 136841217, 505939969, 170526209, 405406469, 539624961, 506331395, 372245762, 338822913]}


def rgb(color):
    return (
        (color >> 16) & 255,
        (color >> 8) & 255,
        color & 255
    )


def prepare_sprite(palette, sprs):
    prepared = {}
    colors = [rgb(c) for c in palette]
    for sprite_id, spr in sprs.items():
        rectangles = []
        for value in spr[1:]:
            px = (value >> 25) & 511
            py = (value >> 17) & 255
            w  = (value >> 8)  & 511
            h  = value & 255
            if w > 0 and h > 0:
                rectangles.append((px, py, w, h))
        prepared[sprite_id] = (colors[spr[0]], rectangles)
    return prepared


_club      = prepare_sprite(club_palette, club_sprites)
_diamond   = prepare_sprite(diamond_palette, diamond_sprites)
_heart     = prepare_sprite(heart_palette, heart_sprites)
_spade     = prepare_sprite(spade_palette, spade_sprites)


def draw_sprite(x, y, prepared):
    for sprite_id in prepared:
        color, rectangles = prepared[sprite_id]
        ti_draw.set_color(*color)
        for px, py, w, h in rectangles:
            ti_draw.fill_rect(x + px - 2, y + py - 2, w + 1, h + 1)


SUITS = [_club, _diamond, _heart, _spade]


def draw_bg():
    ti_draw.set_color(*BG_COLOR)
    ti_draw.fill_rect(-1, -1, SCREEN_WIDTH, SCREEN_HEIGHT)


def draw_footer():
    text = "Press [clear] to exit"
    tw = len(text) * CHAR_W
    tx = (SCREEN_WIDTH - tw) // 2
    ty = SCREEN_HEIGHT - (BUTTON_HEIGHT // 2) + 4
    ti_draw.set_color(*TEXT_COLOR)
    ti_draw.draw_text(tx, ty, text)


def new_cells():
    # Every grid cell, in random order
    cells = [(c, r) for r in range(ROWS) for c in range(COLS)]
    for i in range(len(cells) - 1, 0, -1):
        j = random.randint(0, i)
        cells[i], cells[j] = cells[j], cells[i]
    return cells


def draw_in_cell(col, row):
    # +2 offsets draw_sprite's -2 so the sprite sits exactly in its cell
    x = GRID_X + col * SPRITE_SIZE + 2
    y = GRID_Y + row * SPRITE_SIZE + 2
    draw_sprite(x, y, random.choice(SUITS))


def run_game():
    draw_bg()
    draw_footer()

    cells = new_cells()

    while True:
        key = get_key(0)

        if key == CLEAR_KEY:
            break

        if not cells:
            # Grid is full: wipe it and start filling again
            draw_bg()
            draw_footer()
            cells = new_cells()
        col, row = cells.pop()
        draw_in_cell(col, row)

run_game()
