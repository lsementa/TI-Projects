import ti_draw
from ti_system import *

# Dimensions
SCREEN_WIDTH  = 321
SCREEN_HEIGHT = 211
CHAR_W = 10
SPRITE_W = 43
SPRITE_H = 51

# Colors
BG_COLOR   = (255, 255, 255)
BG_ALT     = (0, 0, 0)
TEXT_COLOR = (255, 0, 0)

# Movement
STEP = 10

# Key codes
K_LEFT  = 24
K_RIGHT = 26
K_UP    = 25
K_DOWN  = 34
K_CLEAR = 45
K_ENTER = 105
K_PAUSE = 21

Dino1_palette = [5460819, 16777215]
Dino1_sprites = {0: [0, 839389195, 772543497, 773720580, 1109526018, 103154188, 707136013, 606735627, 170787338, 506336258, 238158346, 439489031, 1110573570, 305534469, 306189315, 306582018, 373952002, 441320962, 776865026, 441582594, 441844228, 509215234], 1: [1, 906887682]}


def draw_bg():
    ti_draw.set_color(*BG_COLOR)
    ti_draw.fill_rect(-1, -1, SCREEN_WIDTH, SCREEN_HEIGHT)


def rgb(color):
    return (
        (color >> 16) & 255,
        (color >> 8) & 255,
        color & 255
    )


def prepare_sprite(palette, sprs):
    # Returns a list of (color, rects) in draw order. Offsets and sizes are
    # pre-adjusted here so draw_sprite does as little work per frame as possible.
    prepared = []
    colors = [rgb(c) for c in palette]
    for sprite_id in sorted(sprs):
        spr = sprs[sprite_id]
        rectangles = []
        for value in spr[1:]:
            px = (value >> 25) & 511
            py = (value >> 17) & 255
            w  = (value >> 8)  & 511
            h  = value & 255
            if w > 0 and h > 0:
                rectangles.append((px - 2, py - 2, w + 1, h + 1))
        prepared.append((colors[spr[0]], rectangles))
    return prepared


Dino1 = prepare_sprite(Dino1_palette, Dino1_sprites)


def draw_sprite(x, y, prepared):
    set_color = ti_draw.set_color
    fill_rect = ti_draw.fill_rect
    for color, rectangles in prepared:
        set_color(*color)
        for px, py, w, h in rectangles:
            fill_rect(x + px, y + py, w, h)


def draw_info(x, y, bg):
    ti_draw.set_color(*bg)
    ti_draw.fill_rect(0, 0, 130, 14)
    ti_draw.set_color(*TEXT_COLOR)
    ti_draw.draw_text(2, 20, "x:" + str(x) + " y:" + str(y))


def erase_sprite(x, y, bg):
    ti_draw.set_color(*bg)
    ti_draw.fill_rect(x - 2, y - 2, SPRITE_W + 2, SPRITE_H + 2)


def redraw_all(x, y, bg):
    ti_draw.set_color(*bg)
    ti_draw.fill_rect(-1, -1, SCREEN_WIDTH, SCREEN_HEIGHT)
    draw_sprite(x, y, SPRITE)
    draw_info(x, y, bg)


# Sprite to preview - swap this for any prepared sprite
SPRITE = Dino1


def run_game():
    x = (SCREEN_WIDTH - SPRITE_W) // 2
    y = (SCREEN_HEIGHT - SPRITE_H) // 2
    bg = BG_COLOR
    redraw_all(x, y, bg)

    while True:
        key = get_key(0)

        if key == K_CLEAR:
            break

        if key == K_ENTER:
            # Toggle background to check how the sprite looks on light/dark
            bg = BG_ALT if bg == BG_COLOR else BG_COLOR
            redraw_all(x, y, bg)
            continue

        nx, ny = x, y
        if key == K_LEFT:
            nx -= STEP
        elif key == K_RIGHT:
            nx += STEP
        elif key == K_UP:
            ny -= STEP
        elif key == K_DOWN:
            ny += STEP
        else:
            continue

        nx = max(0, min(SCREEN_WIDTH - SPRITE_W, nx))
        ny = max(0, min(SCREEN_HEIGHT - SPRITE_H, ny))
        if (nx, ny) == (x, y):
            continue

        erase_sprite(x, y, bg)
        x, y = nx, ny
        draw_sprite(x, y, SPRITE)
        draw_info(x, y, bg)


run_game()
