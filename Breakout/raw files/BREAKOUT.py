import ti_draw
import random
import time
from ti_system import *
try:
    from micropython import const   # compiled (.8mp2): values built in
except ImportError:
    def const(x):                   # plain .py without micropython
        return x

# Screen
SCREEN_W = const(321)
SCREEN_H = const(211)
SQ       = const(6)
SCORE_H  = const(22)
COLS = const((SCREEN_W - 2) // SQ)
ROWS = const((SCREEN_H - SCORE_H - 2) // SQ)
BRD_X = const((SCREEN_W - COLS * SQ - 2) // 2)
BRD_Y = const(SCORE_H)

PL = const(BRD_X + 2)
PR = const(BRD_X + 2 + COLS * SQ)
PT = const(BRD_Y + 2)
PB = const(BRD_Y + ROWS * SQ)

# Brick grid
B_ROWS       = const(5)
BRICK_COLS   = const(7)
BRICK_W_SLOT = const(45)
BRICK_W      = const(44)
BRICK_H_SLOT = const(10)
BRICK_H      = const(9)
BK_X = const(PL + (COLS * SQ - BRICK_COLS * BRICK_W_SLOT) // 2)
BK_Y = const(PT + 5)

# Colors
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (255, 0,   0)
YELLOW = (255, 255, 0)
GRAY   = (180, 180, 180)

# Key codes
K_LEFT  = const(24)
K_RIGHT = const(26)
K_UP    = const(25)
K_DOWN  = const(34)
K_CLEAR = const(45)
K_ENTER = const(105)
K_PAUSE = const(21)

CHAR_W = const(10)

# Paddle: "wheel" control. Every arrow report from get_key (the press and each
# auto-repeat) is one click that moves a target position, and the paddle
# eases toward the target. No momentum: let go and it stops on the target.
PAD_W      = const(6 * SQ)  # 36 px
PAD_H      = const(SQ)      # 6 px
STEP_MIN   = 8.0        # px per click: a tap, and the first repeats of a hold
STEP_MAX   = 60.0       # px per click after holding RAMP_TIME (repeats come
                        # 10 per second, so 30 px = 300 px/s)
RAMP_TIME  = 0.6        # s of repeats to grow from STEP_MIN to STEP_MAX
GAP_RATE   = 60.0       # px/s the target creeps during the 0.45 s before the
                        # first repeat, so a hold starts moving at once (a tap
                        # drifts ~GAP_RATE * HOLD_FIRST = 15 px past its click)
PAD_EASE   = 0.7        # fraction of the distance to the target covered each
                        # 0.04 s frame (higher = snappier, lower = smoother)
MAX_FRAME  = 0.1        # longer frames are capped

# Ball
BASE_BALL_V = 6.0
BALL_V_MAX  = 10.0
BALL_SZ     = const(6)

# Timing
DT = 0.04               # frame time (ball speed is px per frame)

# Input timing. get_key reports one key at a time, and a held key repeats only
# after a delay (measured with KEYDELAY.py: 0.45 s, then every 0.10 s), so an
# arrow counts as held for a while after each report.
HOLD_FIRST = 0.5        # gap fill lasts this long after a fresh press
KEY_DELAY  = 0.4        # measured: a held key's first repeat comes this late
KEY_REPEAT = 0.10       # measured: ...`then one every this long
KEY_SLOP   = 0.1        # timing tolerance (a slow frame delays a report)

N_PATTERNS = const(6)

# Blue_Brick.png: 44 x 9
Blue_Brick_palette = [255, 8558797]
Blue_Brick_sprites = {0: b'*\x01\x02\x08\x03\x02)\x07\x02\x07*\x02\x01\x08+\x01', 1: b'\x00\x00,\x01\x00\x01*\x01\x00\x02\x03\x05\x00\x07\x02\x01\x00\x08\x01\x01'}

# Green_Brick.png: 44 x 9
Green_Brick_palette = [32768, 8893330]
Green_Brick_sprites = {0: b'*\x01\x02\x08\x03\x02)\x07\x02\x07*\x02\x01\x08+\x01', 1: b'\x00\x00,\x01\x00\x01*\x01\x00\x02\x03\x05\x00\x07\x02\x01\x00\x08\x01\x01'}

# Orange_Brick.png: 44 x 9
Orange_Brick_palette = [16753920, 16631433]
Orange_Brick_sprites = {0: b'+\x00\x01\t*\x01\x02\x08\x03\x02)\x07\x02\x07*\x02\x01\x08+\x01', 1: b'\x00\x00+\x01\x00\x01*\x01\x00\x02\x03\x05\x00\x07\x02\x01\x00\x08\x01\x01'}

# Red_Brick.png: 44 x 9
Red_Brick_palette = [16711680, 16160377]
Red_Brick_sprites = {0: b'+\x00\x01\t*\x01\x02\x08\x03\x02)\x07\x02\x07*\x02\x01\x08+\x01', 1: b'\x00\x00+\x01\x00\x01*\x01\x00\x02\x03\x05\x00\x07\x02\x01\x00\x08\x01\x01'}

# Yellow_Brick.png: 44 x 9
Yellow_Brick_palette = [16771584, 16771989]
Yellow_Brick_sprites = {0: b'*\x01\x02\x08\x03\x02)\x07\x01\x08+\x01', 1: b'\x00\x00,\x01\x00\x01*\x01\x00\x02\x03\x06\x00\x08\x01\x01'}

# Brick sprite per row, top to bottom (top row worth 5 pts, bottom 1)
BRICK_SPRITES = [
    (Red_Brick_palette,    Red_Brick_sprites),
    (Orange_Brick_palette, Orange_Brick_sprites),
    (Yellow_Brick_palette, Yellow_Brick_sprites),
    (Green_Brick_palette,  Green_Brick_sprites),
    (Blue_Brick_palette,   Blue_Brick_sprites),
]

def sc(col):
    ti_draw.set_color(col[0], col[1], col[2])


def clear_all():
    sc(BLACK)
    ti_draw.fill_rect(-1, -1, SCREEN_W + 2, SCREEN_H + 2)


PRACTICE = [False]      # True in Practice mode: unlimited lives, no score


def draw_hud(lives, score, level):
    sc(BLACK)
    ti_draw.fill_rect(0, 0, SCREEN_W, SCORE_H)
    sc(WHITE)
    lv = "LV " + str(level)
    ti_draw.draw_text(SCREEN_W // 2 - len(lv) * CHAR_W // 2, SCORE_H, lv)
    if PRACTICE[0]:
        return                  # score and lives stay blank
    ti_draw.draw_text(5, SCORE_H, str(score))
    lt = str(lives)
    ti_draw.draw_text(SCREEN_W - len(lt) * CHAR_W - 5, SCORE_H, lt)


def draw_sprite(x, y, palette, sprites):
    for c in sprites:
        rgb = palette[c]
        ti_draw.set_color(rgb >> 16, (rgb >> 8) & 255, rgb & 255)
        r = sprites[c]
        for i in range(0, len(r), 4):
            ti_draw.fill_rect(x + r[i] - 1, y + r[i + 1] - 1,
                              r[i + 2] + 1, r[i + 3] + 1)


def make_board(level):
    p = (level - 1) % N_PATTERNS      
    if p == 0:  # Checkerboard
        return [[(r + c) % 2 == 0 for c in range(BRICK_COLS)] for r in range(B_ROWS)]
    if p == 1:  # Diamond
        return [[abs(r - 2) + abs(c - 3) <= 3 for c in range(BRICK_COLS)] for r in range(B_ROWS)]
    if p == 2: # Wall
        return [[True] * BRICK_COLS for _ in range(B_ROWS)]
    if p == 3:  # Fortress
        return [[r == 0 or r == B_ROWS - 1 or c == 0 or c == BRICK_COLS - 1
                 for c in range(BRICK_COLS)] for r in range(B_ROWS)]
    if p == 4:  # Hourglass
        t = [[1,1,1,1,1,1,1],[0,1,1,1,1,1,0],[0,0,1,1,1,0,0],[0,1,1,1,1,1,0],[1,1,1,1,1,1,1]]
        return [[bool(t[r][c]) for c in range(BRICK_COLS)] for r in range(B_ROWS)]
    if p == 5:  # two T's
        t = [[1,1,1,0,1,1,1],[0,1,0,0,0,1,0],[0,1,0,0,0,1,0],[0,1,0,0,0,1,0],[0,0,0,0,0,0,0]]
        return [[bool(t[r][c]) for c in range(BRICK_COLS)] for r in range(B_ROWS)]


def draw_all_bricks(board):
    for r in range(B_ROWS):
        palette, sprites = BRICK_SPRITES[r]
        for c in range(BRICK_COLS):
            if board[r][c]:
                draw_sprite(BK_X + c * BRICK_W_SLOT,
                            BK_Y + r * BRICK_H_SLOT,
                            palette, sprites)


def erase_brick(r, c):
    sc(BLACK)
    # draw_sprite places pixels at x-1, y-1, so erase from there too
    ti_draw.fill_rect(BK_X + c * BRICK_W_SLOT - 1, BK_Y + r * BRICK_H_SLOT - 1,
                      BRICK_W_SLOT, BRICK_H_SLOT)


PAD_DRAWN = [None]     # x the paddle was last drawn at (None = not on screen)


def draw_pad(px, py):
    ipx = int(px + 0.5); ipy = int(py)
    old = PAD_DRAWN[0]
    if old is not None and old != ipx:
        sc(BLACK)
        if abs(ipx - old) >= PAD_W:
            ti_draw.fill_rect(old - 1, ipy, PAD_W + 2, PAD_H)
        elif ipx > old:
            ti_draw.fill_rect(old - 1, ipy, ipx - old + 3, PAD_H)
        else:
            ti_draw.fill_rect(ipx + PAD_W - 2, ipy, old - ipx + 3, PAD_H)
    sc(GRAY)
    ti_draw.fill_rect(ipx, ipy, PAD_W, PAD_H)
    PAD_DRAWN[0] = ipx


def draw_ball(bx, by):
    sc(WHITE)
    ti_draw.fill_rect(int(bx), int(by), BALL_SZ, BALL_SZ)


def erase_ball(bx, by):
    sc(BLACK)
    ti_draw.fill_rect(int(bx), int(by), BALL_SZ, BALL_SZ)


def show_msg(t1, t2, t3):
    clear_all()
    cx = SCREEN_W // 2
    cy = SCREEN_H // 2
    sc(RED)
    ti_draw.draw_text(cx - len(t1) * CHAR_W // 2, cy - 30, t1)
    sc(YELLOW)
    ti_draw.draw_text(cx - len(t2) * CHAR_W // 2, cy, t2)
    sc(WHITE)
    ti_draw.draw_text(cx - len(t3) * CHAR_W // 2, cy + 35, t3)


def new_ball(px, py, v):
    bx = float(px + PAD_W // 2 - BALL_SZ // 2)
    by = float(py - BALL_SZ - 2)
    dx = random.choice([-v, v])
    return bx, by, dx, -v


# INP = [arrow direction (-1/0/1), last arrow report time,
#        fresh arrow press time, arrow is repeating (held), prev key,
#        px of clicks not yet added to the target, direction reversed]
INP = [0, -99.0, -99.0, False, 0, 0.0, False]


def poll():
    # Returns a newly pressed non-arrow key (or 0). Each arrow report is a
    # wheel click, added to INP[5]. A report is a repeat (key held) only if
    # its timing fits the OS auto-repeat, so a double tap is two small clicks.
    k = get_key(0)
    now = time.monotonic()
    new = 0
    if k == K_LEFT or k == K_RIGHT:
        d = -1 if k == K_LEFT else 1
        same = d == INP[0]
        if same and now - INP[1] <= KEY_REPEAT + KEY_SLOP:
            # Next report of a stream. It only proves the key is held once
            # the press is old enough to have repeated (not a doubled tap).
            if now - INP[2] >= KEY_DELAY - KEY_SLOP:
                INP[3] = True
        elif same and abs(now - INP[2] - KEY_DELAY) <= KEY_SLOP:
            INP[3] = True               # first repeat: held
        else:
            INP[2] = now                # fresh press: not known to be held
            INP[3] = False
            if not same:
                INP[6] = True           # turned around: drop the old target
                INP[5] = 0.0
        step = STEP_MIN
        if INP[3]:
            t = (now - INP[2] - KEY_DELAY) / RAMP_TIME
            step += (STEP_MAX - STEP_MIN) * max(0.0, min(1.0, t))
        INP[5] += d * step
        INP[0] = d
        INP[1] = now
    elif k != INP[4]:
        new = k
    INP[4] = k
    return new


def reset_input():
    INP[0] = 0
    INP[3] = False
    INP[5] = 0.0
    INP[6] = False


def run_game():
    level  = 1
    score  = 0
    lives  = 3
    ball_v = BASE_BALL_V

    board  = make_board(level)
    n_left = sum(sum(row) for row in board)

    pad_x  = float(PL + (COLS * SQ - PAD_W) // 2)
    pad_y  = float(PT + (ROWS - 2) * SQ)
    pad_tx = pad_x                  # target the paddle eases toward
    bx, by, dx, dy = new_ball(pad_x, pad_y, ball_v)

    paused = False
    reset_input()

    clear_all()
    PAD_DRAWN[0] = None
    draw_hud(lives, score, level)
    draw_all_bricks(board)
    draw_pad(pad_x, pad_y)
    draw_ball(bx, by)

    tick = time.monotonic()

    while True:
        key = poll()
        now = time.monotonic()

        if key == K_CLEAR:
            return False
        if key == K_PAUSE:
            paused = not paused

        if paused:
            tick = now
            INP[5] = 0.0                # ignore arrows pressed while paused
            continue

        if now - tick < DT:
            continue
        dt = min(now - tick, MAX_FRAME)
        tick = now

        # Paddle: wheel clicks move the target, the paddle eases toward it
        if INP[6]:
            pad_tx = pad_x              # reversing starts from where it is
            INP[6] = False
        pad_tx += INP[5]
        INP[5] = 0.0
        if INP[0] and not INP[3] and now - INP[2] < HOLD_FIRST:
            pad_tx += INP[0] * GAP_RATE * dt   # bridge the repeat delay
        # Clamp so a long hold can't build up travel past the wall
        pad_tx = max(float(PL), min(float(PR - PAD_W), pad_tx))
        pad_x += (pad_tx - pad_x) * (1.0 - (1.0 - PAD_EASE) ** (dt / DT))
        if abs(pad_tx - pad_x) < 0.5:
            pad_x = pad_tx

        erase_ball(bx, by)

        bx += dx
        by += dy

        # Wall bounces
        if bx < PL:
            bx = float(PL)
            dx = abs(dx)
        if bx + BALL_SZ > PR:
            bx = float(PR - BALL_SZ)
            dx = -abs(dx)
        if by < PT:
            by = float(PT)
            dy = abs(dy)

        # Lost life
        if by + BALL_SZ > PB:
            if not PRACTICE[0]:         # Practice: unlimited lives
                lives -= 1
                draw_hud(lives, score, level)
                if lives <= 0:
                    show_msg("GAME OVER", "Score: " + str(score),
                             "[enter] Menu [clear] Quit")
                    return None
            pad_tx = pad_x              # stop the paddle where it is
            reset_input()
            bx, by, dx, dy = new_ball(pad_x, pad_y, ball_v)
            draw_ball(bx, by)
            draw_pad(pad_x, pad_y)
            continue

        # Paddle bounce
        ibx = int(bx); iby = int(by)
        ipx = int(pad_x); ipy = int(pad_y)
        if (dy > 0 and
                iby + BALL_SZ >= ipy and iby < ipy + PAD_H and
                ibx + BALL_SZ > ipx and ibx < ipx + PAD_W):
            rel = (ibx + BALL_SZ // 2) - (ipx + PAD_W // 2)
            dx  = rel / (PAD_W * 0.5) * ball_v * 1.4
            if abs(dx) < 0.4:
                dx = 0.4 if dx >= 0 else -0.4
            dy  = -abs(dy)
            spd = (dx * dx + dy * dy) ** 0.5
            dx  = dx / spd * ball_v
            dy  = dy / spd * ball_v

        # Brick collision
        ibx = int(bx); iby = int(by)
        hit = set()
        for ex in [ibx, ibx + BALL_SZ - 1]:
            for ey in [iby, iby + BALL_SZ - 1]:
                gc = (ex - BK_X) // BRICK_W_SLOT
                gr = (ey - BK_Y) // BRICK_H_SLOT
                if 0 <= gr < B_ROWS and 0 <= gc < BRICK_COLS:
                    lx = (ex - BK_X) % BRICK_W_SLOT
                    ly = (ey - BK_Y) % BRICK_H_SLOT
                    if lx < BRICK_W and ly < BRICK_H and board[gr][gc]:
                        hit.add((gr, gc))

        if hit:
            flip_x = flip_y = False
            for (gr, gc) in hit:
                board[gr][gc] = False
                erase_brick(gr, gc)
                score  += B_ROWS - gr   # top row=5pt, bottom row=1pt
                n_left -= 1
                kx = BK_X + gc * BRICK_W_SLOT
                ky = BK_Y + gr * BRICK_H_SLOT
                ox = min(ibx + BALL_SZ - kx, kx + BRICK_W - ibx)
                oy = min(iby + BALL_SZ - ky, ky + BRICK_H - iby)
                if ox < oy:
                    flip_x = True
                else:
                    flip_y = True
            if flip_x:
                dx = -dx
            if flip_y:
                dy = -dy
            draw_hud(lives, score, level)

        draw_ball(bx, by)
        draw_pad(pad_x, pad_y)

        if n_left <= 0:
            level += 1
            ball_v = min(BASE_BALL_V * (1.1 ** (level - 1)), BALL_V_MAX)
            board  = make_board(level)
            n_left = sum(sum(row) for row in board)
            pad_tx = pad_x              # stop the paddle where it is
            reset_input()
            erase_ball(bx, by)
            sc(BLACK)
            ti_draw.fill_rect(BK_X - 1, BK_Y - 1,
                               BRICK_COLS * BRICK_W_SLOT,
                               B_ROWS * BRICK_H_SLOT)
            draw_all_bricks(board)
            bx, by, dx, dy = new_ball(pad_x, pad_y, ball_v)
            draw_ball(bx, by)
            draw_hud(lives, score, level)


# Big title letters, 5 x 7 pixel grid, drawn TITLE_SCALE times bigger
TITLE_SCALE = const(6)
TITLE_FONT = {
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
}
TITLE_Y   = const(14)           # top of the big "BREAKOUT"
BAND_Y    = const(70)           # row of bricks under the title
MENU_Y    = const(130)          # first menu option
MENU_STEP = const(26)           # space between options
MENU      = ["Play", "Practice"]
HINT      = "[enter] Select [clear] Quit"

_last_key = [0]


def read_key():
    # Waits for a new key press and returns its code
    while True:
        k = get_key(0)
        if k != _last_key[0]:
            _last_key[0] = k
            if k:
                return k


def fill_box(x, y, w, h):
    # fill_rect draws 1 px short, so shift and grow it (same as draw_sprite)
    ti_draw.fill_rect(x - 1, y - 1, w + 1, h + 1)


def draw_big_text(text, y):
    # Centered block letters, each in the next brick color. Each row of a
    # letter is drawn as runs of filled pixels: a handful of rects a letter.
    s = TITLE_SCALE
    x = (SCREEN_W - (len(text) * 6 - 1) * s) // 2
    for n, ch in enumerate(text):
        rgb = BRICK_SPRITES[n % B_ROWS][0][0]
        ti_draw.set_color(rgb >> 16, (rgb >> 8) & 255, rgb & 255)
        for r, line in enumerate(TITLE_FONT[ch]):
            c = 0
            while c < 5:
                if line[c] == "#":
                    start = c
                    while c < 5 and line[c] == "#":
                        c += 1
                    fill_box(x + start * s, y + r * s, (c - start) * s, s)
                else:
                    c += 1
        x += 6 * s


def draw_text_centered(y, text, color):
    sc(color)
    ti_draw.draw_text(SCREEN_W // 2 - len(text) * CHAR_W // 2, y, text)


def draw_brackets(i, color):
    # "[" and "]" around option i, lined up for every option. Drawing them
    # again in BLACK erases them.
    longest = max(len(t) for t in MENU)
    x = SCREEN_W // 2 - longest * CHAR_W // 2
    y = MENU_Y + i * MENU_STEP
    sc(color)
    ti_draw.draw_text(x - CHAR_W - 6, y, "[")
    ti_draw.draw_text(x + longest * CHAR_W + 6, y, "]")


def title_screen(sel=0):
    # Returns the picked option (0 = Play, 1 = Practice), or None if CLEAR
    # is pressed.
    clear_all()
    draw_big_text("BREAKOUT", TITLE_Y)
    for c in range(BRICK_COLS):     # one brick of each color under the title
        palette, sprites = BRICK_SPRITES[c % B_ROWS]
        draw_sprite(BK_X + c * BRICK_W_SLOT, BAND_Y, palette, sprites)
    for i in range(len(MENU)):
        draw_text_centered(MENU_Y + i * MENU_STEP, MENU[i], WHITE)
    draw_text_centered(SCREEN_H - 4, HINT, GRAY)
    draw_brackets(sel, YELLOW)
    while True:
        key = read_key()
        if key == K_ENTER:
            return sel
        if key == K_CLEAR:
            return None
        new_sel = sel
        if key == K_UP and sel > 0:
            new_sel -= 1
        elif key == K_DOWN and sel < len(MENU) - 1:
            new_sel += 1
        if new_sel != sel:
            draw_brackets(sel, BLACK)       # erase old brackets
            sel = new_sel
            draw_brackets(sel, YELLOW)


# Main loop: menu -> game. CLEAR in a game goes back to the menu, CLEAR on
# the menu (or after GAME OVER) quits.
mode = 0
while True:
    mode = title_screen(mode)
    if mode is None:
        break
    PRACTICE[0] = mode == 1
    if run_game() is None:              # GAME OVER: [enter] menu, [clear] quit
        key = 0
        while key != K_ENTER and key != K_CLEAR:
            key = read_key()
        if key == K_CLEAR:
            break
