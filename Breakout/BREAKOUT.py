import ti_draw
import random
import time
from ti_system import *

# Screen
SCREEN_W = 321
SCREEN_H = 211
SQ       = 6
SCORE_H  = 22
COLS = (SCREEN_W - 2) // SQ
ROWS = (SCREEN_H - SCORE_H - 2) // SQ
BRD_X = (SCREEN_W - COLS * SQ - 2) // 2
BRD_Y = SCORE_H

PL = BRD_X + 2
PR = BRD_X + 2 + COLS * SQ
PT = BRD_Y + 2
PB = BRD_Y + ROWS * SQ

# Brick grid
B_ROWS       = 5
BRICK_COLS   = 7
BRICK_W_SLOT = 45
BRICK_W      = 44
BRICK_H_SLOT = 10
BRICK_H      = 9
BK_X = PL + (COLS * SQ - BRICK_COLS * BRICK_W_SLOT) // 2
BK_Y = PT + 5

# Colors
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (255, 0,   0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN  = (0,   220, 0)
BLUE   = (0,   100, 255)
GRAY   = (180, 180, 180)
BRICKS = [RED, ORANGE, YELLOW, GREEN, BLUE]  # row 0-4, worth 1-5 pts

# Key codes
K_LEFT  = 24
K_RIGHT = 26
K_CLEAR = 45
K_ENTER = 105
K_PAUSE = 21

CHAR_W = 10

# Paddle
PAD_W     = 6 * SQ      # 36 px
PAD_H     = SQ          # 6 px
PAD_MAX   = 25          # max velocity px/frame
PAD_ACCEL = 6           # velocity gained per frame when holding
PAD_FRIC  = 0.75         # velocity multiplier each frame on release
PAD_WING  = PAD_MAX + 2 # 14 px black erasure strips

# Ball
BASE_BALL_V = 6.0
BALL_V_MAX  = 10.0
BALL_SZ     = 6

# Timing
DT       = 0.04
HOLD_EXT = 0.04

N_PATTERNS = 6


def sc(col):
    ti_draw.set_color(col[0], col[1], col[2])


def clear_all():
    sc(BLACK)
    ti_draw.fill_rect(-1, -1, SCREEN_W + 2, SCREEN_H + 2)


def draw_hud(lives, score, level):
    sc(BLACK)
    ti_draw.fill_rect(0, 0, SCREEN_W, SCORE_H)
    sc(WHITE)
    ti_draw.draw_text(5, SCORE_H, str(score))
    lv = "LV " + str(level)
    ti_draw.draw_text(SCREEN_W // 2 - len(lv) * CHAR_W // 2, SCORE_H, lv)
    lt = str(lives)
    ti_draw.draw_text(SCREEN_W - len(lt) * CHAR_W - 5, SCORE_H, lt)


def make_board(level):
    p = (level - 1) % N_PATTERNS
    if p == 0:  # Wall
        return [[True] * BRICK_COLS for _ in range(B_ROWS)]
    if p == 1:  # Checkerboard
        return [[(r + c) % 2 == 0 for c in range(BRICK_COLS)] for r in range(B_ROWS)]
    if p == 2:  # Diamond
        return [[abs(r - 2) + abs(c - 3) <= 3 for c in range(BRICK_COLS)] for r in range(B_ROWS)]
    if p == 3:  # Fortress
        return [[r == 0 or r == B_ROWS - 1 or c == 0 or c == BRICK_COLS - 1
                 for c in range(BRICK_COLS)] for r in range(B_ROWS)]
    if p == 4:  # Hourglass
        t = [[1,1,1,1,1,1,1],[0,1,1,1,1,1,0],[0,0,1,1,1,0,0],[0,1,1,1,1,1,0],[1,1,1,1,1,1,1]]
        return [[bool(t[r][c]) for c in range(BRICK_COLS)] for r in range(B_ROWS)]
    # p == 5: two T's
    t = [[1,1,1,0,1,1,1],[0,1,0,0,0,1,0],[0,1,0,0,0,1,0],[0,1,0,0,0,1,0],[0,0,0,0,0,0,0]]
    return [[bool(t[r][c]) for c in range(BRICK_COLS)] for r in range(B_ROWS)]


def draw_all_bricks(board):
    for r in range(B_ROWS):
        sc(BRICKS[r])
        for c in range(BRICK_COLS):
            if board[r][c]:
                ti_draw.fill_rect(
                    BK_X + c * BRICK_W_SLOT,
                    BK_Y + r * BRICK_H_SLOT,
                    BRICK_W, BRICK_H
                )


def erase_brick(r, c):
    sc(BLACK)
    ti_draw.fill_rect(BK_X + c * BRICK_W_SLOT, BK_Y + r * BRICK_H_SLOT,
                      BRICK_W_SLOT, BRICK_H_SLOT)


def draw_pad(px, py):
    ipx = int(px); ipy = int(py)
    sc(BLACK)
    ti_draw.fill_rect(ipx - PAD_WING, ipy, PAD_WING, PAD_H)
    ti_draw.fill_rect(ipx + PAD_W,    ipy, PAD_WING, PAD_H)
    sc(GRAY)
    ti_draw.fill_rect(ipx,            ipy, PAD_W,    PAD_H)


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


def run_game():
    level  = 1
    score  = 0
    lives  = 3
    ball_v = BASE_BALL_V

    board  = make_board(level)
    n_left = sum(sum(row) for row in board)

    pad_x  = float(PL + (COLS * SQ - PAD_W) // 2)
    pad_y  = float(PT + (ROWS - 2) * SQ)
    pad_vx = 0.0
    bx, by, dx, dy = new_ball(pad_x, pad_y, ball_v)

    paused   = False
    key_held = 0
    key_time = 0.0
    prev_raw = 0

    clear_all()
    draw_hud(lives, score, level)
    draw_all_bricks(board)
    draw_pad(pad_x, pad_y)
    draw_ball(bx, by)

    tick = time.monotonic()

    while True:
        raw = get_key(0)
        now = time.monotonic()

        if raw != prev_raw:
            if raw == K_CLEAR:
                return False
            if raw == K_PAUSE:
                paused = not paused
        prev_raw = raw

        if raw == K_LEFT or raw == K_RIGHT:
            key_held = raw
            key_time = now + HOLD_EXT
        elif now >= key_time:
            key_held = 0

        if paused:
            continue

        if now - tick < DT:
            continue
        tick = now

        # Paddle momentum: accelerate while held, friction on release
        if key_held == K_LEFT:
            pad_vx = max(-PAD_MAX, pad_vx - PAD_ACCEL)
        elif key_held == K_RIGHT:
            pad_vx = min(PAD_MAX, pad_vx + PAD_ACCEL)
        else:
            pad_vx *= PAD_FRIC
            if abs(pad_vx) < 0.5:
                pad_vx = 0.0

        new_px = max(float(PL), min(float(PR - PAD_W), pad_x + pad_vx))
        if new_px == float(PL) and pad_vx < 0:
            pad_vx = 0.0
        elif new_px == float(PR - PAD_W) and pad_vx > 0:
            pad_vx = 0.0
        pad_x = new_px

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
            lives -= 1
            draw_hud(lives, score, level)
            if lives <= 0:
                show_msg("GAME OVER", "Score: " + str(score), "[enter] / [clear]")
                return None
            pad_vx = 0.0
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
            pad_vx = 0.0
            erase_ball(bx, by)
            sc(BLACK)
            ti_draw.fill_rect(BK_X, BK_Y,
                               BRICK_COLS * BRICK_W_SLOT,
                               B_ROWS * BRICK_H_SLOT)
            draw_all_bricks(board)
            bx, by, dx, dy = new_ball(pad_x, pad_y, ball_v)
            draw_ball(bx, by)
            draw_hud(lives, score, level)


# Main loop
while True:
    result = run_game()
    if result is False:
        break
    while True:
        k = get_key(0)
        if k == K_ENTER:
            break
        if k == K_CLEAR:
            result = False
            break
    if result is False:
        break
