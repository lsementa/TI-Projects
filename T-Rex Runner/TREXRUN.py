import ti_draw
import ti_graphics
import ti_image
import random
import time
from ti_system import *

# Sprites are calculator images drawn with ti_graphics.drawImage. Send
# TREXRUN.py and every file in images/ to the calculator.

# Dimensions
SCREEN_WIDTH  = 321
SCREEN_HEIGHT = 211
IMG_RIGHT = 320         # images are kept fully on screen: x + w <= this
CHAR_W   = 10
GROUND_Y = 150          # y of the horizon line
DINO_X   = 24
MSG_Y    = 62           # first line of centered messages

# Colors
BG_COLOR   = (255, 255, 255)
FG_COLOR   = (83, 83, 83)
TEXT_COLOR = FG_COLOR

# Keyboard Codes
K_UP    = 25
K_DOWN  = 34
K_CLEAR = 45
K_ENTER = 105
K_SCND  = 21

# Everything below is in real time (seconds, pixels per second), so the game
# plays at the same speed no matter how fast the calculator can draw.
SUB_DT      = 0.02      # physics step; collisions are checked every step
MAX_FRAME   = 0.25      # longer frames are capped (game slows instead of skipping)
HOLD_EXT    = 0.3       # duck stays active this long after a repeated [down] report
DUCK_FIRST  = 0.6       # ...and this long after the first one, to cover the delay
                        # before the calculator starts repeating a held key
JUMP_BUFFER = 0.25      # a jump pressed this long before landing still counts

# Physics
JUMP_V      = 200.0     # px/s
GRAVITY     = 450.0     # px/s^2
FAST_FALL   = 1125.0    # gravity while holding [down] in the air
START_SPEED = 100.0     # px/s
MAX_SPEED   = 250.0
SPEED_UP    = 2.0       # px/s gained every second

# Gameplay
SCORE_RATE   = 10.0     # points per second
SCORE_EVERY  = 0.5      # seconds between score display refreshes
PTERO_SCORE  = 150      # pterodactyls start appearing at this score
PTERO_CHANCE = 0.3
PTERO_LIFTS  = [2, 12, 26]  # px above ground: jump / duck / free pass
# Obstacle gap, in seconds of travel at START_SPEED (105-200 px). The gap stays
# that many pixels as the game speeds up, and the jump speeds up with the game
# (same height, shorter airtime), so faster = more obstacles on screen at once.
GAP_MIN = 1.05
GAP_MAX = 2.0
HIT_INSET  = 3          # shrink hitboxes so near-misses feel fair
LEG_SWAP   = 0.15       # seconds per running leg swap
FLAP_SWAP  = 0.3        # seconds per ptero wing flap

# Clouds (background, kept above the dino's jump height)
CLOUD_MAX   = 2
CLOUD_SPEED = 25.0      # px/s
CLOUD_EVERY = 1.0       # seconds between cloud redraws (one cloud at a time)
CLOUD_GAP_MIN = 4.0     # seconds between new clouds
CLOUD_GAP_MAX = 9.0

# Dirt specks under the ground line (move with the obstacles)
DIRT_Y_MIN   = GROUND_Y + 3
DIRT_Y_MAX   = GROUND_Y + 11
DIRT_GAP_MIN = 50.0     # px between specks
DIRT_GAP_MAX = 200.0

# Images: name, width, height, content box (x0, y0, x1, y1)
IMAGES = {
    "RUN1"  : ('TRRUN1', 20, 21, (0, 0, 20, 21)),
    "RUN2"  : ('TRRUN2', 20, 21, (0, 0, 20, 21)),
    "DUCK1" : ('TRDUCK1', 28, 13, (0, 0, 28, 13)),
    "DUCK2" : ('TRDUCK2', 28, 13, (0, 0, 28, 13)),
    "JUMPU" : ('TRJUMPU', 20, 37, (0, 0, 20, 21)),
    "JUMPD" : ('TRJUMPD', 20, 37, (0, 16, 20, 37)),
    "JUMP0" : ('TRJUMP0', 20, 21, (0, 0, 20, 21)),
    "CACT1" : ('TRCACT1', 41, 24, (0, 0, 25, 24)),
    "CACT2" : ('TRCACT2', 27, 24, (0, 0, 11, 24)),
    "CACT3" : ('TRCACT3', 40, 23, (0, 0, 24, 23)),
    "CACT4" : ('TRCACT4', 41, 16, (0, 0, 25, 16)),
    "CACT5" : ('TRCACT5', 32, 16, (0, 0, 16, 16)),
    "CACT6" : ('TRCACT6', 24, 16, (0, 0, 8, 16)),
    "PTERO1": ('TRPTER1', 37, 15, (0, 0, 21, 15)),
    "PTERO2": ('TRPTER2', 37, 15, (0, 0, 21, 15)),
}
RUN    = [IMAGES["RUN1"], IMAGES["RUN2"]]
DUCK   = [IMAGES["DUCK1"], IMAGES["DUCK2"]]
JUMPU  = IMAGES["JUMPU"]
JUMPD  = IMAGES["JUMPD"]
JUMP0  = IMAGES["JUMP0"]
CACTI  = [IMAGES["CACT%d" % i] for i in range(1, 7)]
PTERO  = [IMAGES["PTERO1"], IMAGES["PTERO2"]]
JUMP_H = JUMP0[2]
PAD_V  = JUMPD[3][1]

CLOUD = ('TRCLOUD', 74, 13, (0, 0, 48, 13))

JUMP_PEAK   = 51
CLOUD_Y_MIN = 24
CLOUD_Y_MAX = GROUND_Y - JUMP_PEAK - JUMP_H - PAD_V - CLOUD[2] - 2
CLOUD_X_MAX = IMG_RIGHT - CLOUD[1]      # images must stay fully on screen


# --- Drawing ----------------------------------------------------------------

# ti_graphics images are drawn this far from the matching ti_draw coordinates.
IMG_OFS_X = 0
IMG_OFS_Y = 30

_color = [None]


def color(c):
    if c != _color[0]:
        ti_draw.set_color(c[0], c[1], c[2])
        _color[0] = c


def IMG(e, x, y):
    ti_graphics.drawImage(e[0], x + IMG_OFS_X, y + IMG_OFS_Y)
    _color[0] = None


def clip(x, y, w, h):
    # (x, y, w, h) clipped to the screen, or None if nothing is left.
    if x < 0:
        w += x
        x = 0
    if y < 0:
        h += y
        y = 0
    if x + w > SCREEN_WIDTH:
        w = SCREEN_WIDTH - x
    if y + h > SCREEN_HEIGHT:
        h = SCREEN_HEIGHT - y
    if w > 0 and h > 0:
        return x, y, w, h
    return None


def px_rect(x, y, w, h):
    # Fill exactly the pixels [x, x+w) x [y, y+h) in the current color.
    r = clip(x, y, w, h)
    if r:
        ti_draw.fill_rect(r[0] - 1, r[1] - 1, r[2] + 1, r[3] + 1)


def px_clear(x, y, w, h):
    # Clear exactly the pixels [x, x+w) x [y, y+h) to the (white) background.
    # clear_image includes both corners, hence w - 1 / h - 1. It rejects a
    # 0 width or height, so 1-pixel-wide/tall areas (specks) use fill_rect.
    # clear_image also resets the drawing color to black, so the color cache
    # is invalidated.
    r = clip(x, y, w, h)
    if r:
        if r[2] > 1 and r[3] > 1:
            ti_image.clear_image(r[0], r[1], r[2] - 1, r[3] - 1)
            _color[0] = None
        else:
            color(BG_COLOR)
            ti_draw.fill_rect(r[0] - 1, r[1] - 1, r[2] + 1, r[3] + 1)


def draw_bg():
    ti_image.clear_image()
    _color[0] = None
    color(FG_COLOR)
    px_rect(0, GROUND_Y, SCREEN_WIDTH, 1)
    SCORE_TXT[0] = SCORE_TXT[1] = None    # the clear wiped the HUD text too


# --- Boxes ------------------------------------------------------------------
# A box is (x0, y0, x1, y1) in screen pixels, x1/y1 exclusive.

def img_box(e, x, y):
    return (x, y, x + e[1], y + e[2])


def content_box(e, x, y):
    b = e[3]
    return (x + b[0], y + b[1], x + b[2], y + b[3])


def touch(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def erase(b):
    # Background over a box. Never below the line's row: nothing is drawn
    # there except the jumping dino's padding, which repairs the line itself.
    y1 = min(b[3], GROUND_Y)
    if b[2] > b[0] and y1 > b[1]:
        px_clear(b[0], b[1], b[2] - b[0], y1 - b[1])


def erase_diff(old, new):
    # Erase the part of `old` that `new` (about to be drawn) won't cover.
    # Thanks to the padding this is usually nothing.
    if old is None:
        return
    if new is None or not touch(old, new):
        erase(old)
        return
    if old[1] < new[1]:
        erase((old[0], old[1], old[2], new[1]))
    if old[3] > new[3]:
        erase((old[0], new[3], old[2], old[3]))
    y0 = max(old[1], new[1])
    y1 = min(old[3], new[3])
    if old[0] < new[0]:
        erase((old[0], y0, new[0], y1))
    if old[2] > new[2]:
        erase((new[2], y0, old[2], y1))


# --- HUD and messages -------------------------------------------------------

SCORE_W = 14 * CHAR_W + 4     # "HI 00000 00000"


HI_X  = SCREEN_WIDTH - SCORE_W           # "HI 00000"
NOW_X = HI_X + 9 * CHAR_W               # current score after it
SCORE_TXT = [None, None]      # text on screen: [hi part, current score]


def put_text(slot, x, s):
    # Redraw one HUD field only when its text changes. The old text is
    # overdrawn in the background color, so only glyph pixels change.
    old = SCORE_TXT[slot]
    if old == s:
        return
    if old is not None:
        color(BG_COLOR)
        ti_draw.draw_text(x, 22, old)
    color(TEXT_COLOR)
    ti_draw.draw_text(x, 22, s)
    SCORE_TXT[slot] = s


def draw_score(score, hi):
    put_text(0, HI_X, "HI %05d" % hi)
    put_text(1, NOW_X, "%05d" % score)


def draw_msg(lines):
    color(TEXT_COLOR)
    y = MSG_Y + 10
    for t in lines:
        ti_draw.draw_text(SCREEN_WIDTH // 2 - len(t) * CHAR_W // 2, y, t)
        y += 24


def erase_msg():
    px_clear(0, MSG_Y - 20, SCREEN_WIDTH, 76)


# --- Input ------------------------------------------------------------------
# Polled several times per frame so presses aren't lost during slow frames.
# INP = [time of last [up], duck-until time, quit, pause presses, previous key]
INP = [-99.0, 0.0, False, 0, 0]


def poll():
    k = get_key(0)
    if k == 0:
        INP[4] = 0
        return
    if k == K_UP:
        INP[0] = time.monotonic()
    elif k == K_DOWN:
        now = time.monotonic()
        INP[1] = now + (HOLD_EXT if now < INP[1] else DUCK_FIRST)
    elif k != INP[4]:
        if k == K_CLEAR:
            INP[2] = True
        elif k == K_SCND:
            INP[3] += 1
    INP[4] = k


def wait_for(keys):
    # Waits for a fresh press of one of `keys`. Returns False on [clear].
    prev = get_key(0)
    while True:
        k = get_key(0)
        if k != prev:
            if k == K_CLEAR:
                return False
            if k in keys:
                return True
        prev = k


# --- Game ---------------------------------------------------------------------

def rand_between(a, b):
    return a + (b - a) * random.random()


def spawn(score):
    # Obstacle: [x, y, frames, drawn box or None]. Starts fully on screen.
    if score >= PTERO_SCORE and random.random() < PTERO_CHANCE:
        e = PTERO[0]
        y = GROUND_Y - random.choice(PTERO_LIFTS) - e[2]
        return [float(IMG_RIGHT - e[1]), y, PTERO, None]
    e = random.choice(CACTI)
    return [float(IMG_RIGHT - e[1]), GROUND_Y - e[2], [e], None]


def dino_pose(dino_h, vy, ducking, t):
    # (image, y of the image's top) - padding goes on the side the dino
    # moves away from: below while rising, above while falling.
    if dino_h > 0:
        top = GROUND_Y - int(dino_h) - JUMP_H
        if vy > 0:
            return JUMPU, top
        return JUMPD, top - PAD_V
    e = (DUCK if ducking else RUN)[int(t / LEG_SWAP) & 1]
    return e, GROUND_Y - e[2]


def new_cloud(x):
    # [x, y, drawn box or None]
    return [float(x), random.randint(CLOUD_Y_MIN, CLOUD_Y_MAX), None]


def draw_cloud(c):
    # Draw the cloud at its current x, erasing whatever part of its old
    # position the new image won't cover. Returns False once it has reached
    # the left edge (it is erased and should be dropped).
    x = int(c[0])
    if x < 0:
        if c[2]:
            erase(c[2])
        return False
    box = img_box(CLOUD, x, c[1])
    erase_diff(c[2], box)
    IMG(CLOUD, x, c[1])
    c[2] = box
    return True


def new_speck(x):
    # [x, y, width, drawn x or None]
    return [float(x), random.randint(DIRT_Y_MIN, DIRT_Y_MAX), random.randint(1, 3), None]


def draw_specks(specks, lo=0, hi=0, bottom=0):
    # Move the specks that changed pixel (and any under [lo, hi) down to
    # `bottom`, which the dino's padding just painted over). Erase pass
    # first, then draw pass, so the color is only set once.
    redo = []
    for s in specks:
        old = s[3]
        x = int(s[0])
        if old is not None and x == old and not (old < hi and old + s[2] > lo and s[1] < bottom):
            continue
        redo.append(s)
    if not redo:
        return
    for s in redo:
        if s[3] is not None:
            px_clear(s[3], s[1], s[2], 1)
    color(FG_COLOR)
    for s in redo:
        x = int(s[0])
        px_rect(x, s[1], s[2], 1)       # clipped: off-screen parts vanish
        s[3] = x


def run_game(hi, show_title):
    # Returns the final score, or None if the player quit with [clear].
    draw_bg()
    clouds = [new_cloud(random.randint(20, 90)), new_cloud(random.randint(170, CLOUD_X_MAX))]
    specks = []
    x = rand_between(0, DIRT_GAP_MAX)
    while x < SCREEN_WIDTH:
        specks.append(new_speck(x))
        x += rand_between(DIRT_GAP_MIN, DIRT_GAP_MAX)
    dirt_gap = x - SCREEN_WIDTH
    draw_specks(specks)
    draw_score(0, hi)
    e, y = dino_pose(0, 0, False, 0)
    IMG(e, DINO_X, y)
    for c in clouds:
        draw_cloud(c)

    if show_title:
        draw_msg(["T-REX RUNNER", "[up] jump  [down] duck", "press [up] to start"])
        if not wait_for((K_UP, K_ENTER)):
            return None
        erase_msg()

    INP[0] = -99.0
    INP[1] = 0.0
    INP[2] = False
    INP[3] = 0

    speed      = START_SPEED
    score      = 0.0
    t          = 0.0       # game time (stops while paused)
    dino_h     = 0.0
    vy         = 0.0
    obstacles  = []
    next_gap   = 80.0
    cloud_gap  = rand_between(CLOUD_GAP_MIN, CLOUD_GAP_MAX)
    cloud_turn = 0
    next_cloud = CLOUD_EVERY
    next_score = 0.0
    dead       = False
    old_e      = e
    old_dbox   = img_box(e, DINO_X, y)
    redraw_all = show_title     # the message erase cut through the clouds

    last = time.monotonic()

    while not dead:
        poll()
        if INP[2]:
            return None

        if INP[3]:
            INP[3] = 0
            draw_msg(["PAUSED"])
            while not INP[3] and not INP[2]:
                poll()
            if INP[2]:
                return None
            INP[3] = 0
            erase_msg()
            redraw_all = True
            last = time.monotonic()

        if redraw_all:
            # Everything gets drawn fresh at its current position.
            redraw_all = False
            draw_bg()
            for ob in obstacles:
                ob[3] = None
            for c in clouds:
                c[2] = None
            for s in specks:
                s[3] = None
            old_dbox = None
            old_e = None
            next_score = t

        now = time.monotonic()
        dt = min(now - last, MAX_FRAME)
        prev_start = last
        last = now
        # A jump pressed at any point during the last frame (which can be slow)
        # or within JUMP_BUFFER seconds still counts when the dino lands.
        want_jump = INP[0] >= prev_start or now - INP[0] < JUMP_BUFFER

        # Physics in small steps so nothing tunnels through at low fps
        steps = int(dt / SUB_DT) + 1
        h = dt / steps
        ducking = now < INP[1]
        for _ in range(steps):
            t += h
            pace = speed / START_SPEED      # jump runs this much faster
            if want_jump and dino_h <= 0 and vy <= 0:
                vy = JUMP_V * pace
                INP[0] = -99.0
                want_jump = False
            if dino_h > 0 or vy > 0:
                dino_h += vy * h
                vy -= (FAST_FALL if ducking else GRAVITY) * pace * pace * h
                if dino_h <= 0:
                    dino_h = 0.0
                    vy = 0.0

            move = speed * h
            for ob in obstacles:
                ob[0] -= move
            next_gap -= move
            if next_gap <= 0:
                obstacles.append(spawn(score))
                next_gap = START_SPEED * rand_between(GAP_MIN, GAP_MAX)
            for s in specks:
                s[0] -= move
            dirt_gap -= move
            if dirt_gap <= 0:
                specks.append(new_speck(SCREEN_WIDTH - 1))
                dirt_gap = rand_between(DIRT_GAP_MIN, DIRT_GAP_MAX)
            for c in clouds:
                c[0] -= CLOUD_SPEED * h

            # Collision (inset hitboxes)
            e, y = dino_pose(dino_h, vy, ducking, t)
            d = content_box(e, DINO_X, y)
            for ob in obstacles:
                o = content_box(ob[2][0], int(ob[0]), ob[1])
                if (o[0] + HIT_INSET < d[2] - HIT_INSET and o[2] - HIT_INSET > d[0] + HIT_INSET and
                        o[1] + HIT_INSET < d[3] - HIT_INSET and o[3] - HIT_INSET > d[1] + HIT_INSET):
                    dead = True
            if dead:
                break

            score += SCORE_RATE * h
            speed = min(MAX_SPEED, speed + SPEED_UP * h)

        # --- Draw ---
        # 1) erase only what the new images won't cover (usually nothing),
        # 2) draw the images: clouds, obstacles, then the dino on top,
        # 3) repair the ground line and write the score.
            flap = int(t / FLAP_SWAP) & 1

        # New positions
        live = []
        for ob in obstacles:
            x = int(ob[0])
            if x < 0:
                if ob[3]:
                    erase(ob[3])        # leaves at the left edge
                continue
            fr = ob[2][flap % len(ob[2])]
            live.append((ob, fr, x, img_box(fr, x, ob[1])))
        obstacles = [item[0] for item in live]

        e, dy = dino_pose(dino_h, vy, ducking, t)
        dbox = img_box(e, DINO_X, dy)
        if e is not JUMP0 and e[3][3] - e[3][1] != e[2]:
            # The padding would paint white over an obstacle: use the
            # unpadded image and erase the difference instead.
            for ob, fr, x, box in live:
                if touch(dbox, content_box(fr, x, ob[1])):
                    e = JUMP0
                    dy = GROUND_Y - int(dino_h) - JUMP_H
                    dbox = img_box(e, DINO_X, dy)
                    break
        dino_redraw = e is not old_e or dbox != old_dbox
        for ob, fr, x, box in live:
            if touch(box, dbox) or (ob[3] and touch(ob[3], dbox)):
                dino_redraw = True      # obstacle drawing would cut the dino

        cloud = None
        if clouds and t >= next_cloud:
            cloud_turn = (cloud_turn + 1) % len(clouds)
            cloud = clouds[cloud_turn]
            next_cloud = t + CLOUD_EVERY
        for c in clouds:
            if c[2] is None:
                cloud = c           # never drawn yet (or after a full redraw)
        hud = t >= next_score or dead

        # 1) Erase
        for ob, fr, x, box in live:
            erase_diff(ob[3], box)
        if dino_redraw:
            erase_diff(old_dbox, dbox)

        # 2) Cloud, then images
        if cloud is not None and not draw_cloud(cloud):
            clouds.remove(cloud)            # reached the left edge
        for ob, fr, x, box in live:
            IMG(fr, x, ob[1])
            ob[3] = box
            poll()
        if dino_redraw:
            IMG(e, DINO_X, dy)
            old_e, old_dbox = e, dbox

        # 3) Line and text
        if dino_redraw and dbox[3] > GROUND_Y:
            color(FG_COLOR)                 # rising dino's padding hit the line
            px_rect(DINO_X, GROUND_Y, e[1], 1)
            draw_specks(specks, DINO_X, DINO_X + e[1], dbox[3])   # ...and the dirt
        else:
            draw_specks(specks)
        # Drop specks that have scrolled off the left edge (already erased).
        specks = [s for s in specks if s[0] + s[2] > 0]
        if hud:
            # Erase and redraw back to back so the score is never blank
            # while the images are being drawn.
            draw_score(int(score), hi)
            next_score = t + SCORE_EVERY

        cloud_gap -= dt
        if cloud_gap <= 0 and len(clouds) < CLOUD_MAX:
            clouds.append(new_cloud(CLOUD_X_MAX))
            cloud_gap = rand_between(CLOUD_GAP_MIN, CLOUD_GAP_MAX)

    return int(score)


def main():
    hi = 0
    first = True
    while True:
        result = run_game(hi, first)
        first = False
        if result is None:
            break
        hi = max(hi, result)
        draw_score(result, hi)
        draw_msg(["GAME OVER", "Score: " + str(result), "[up] / [clear]"])
        time.sleep(0.4)
        if not wait_for((K_ENTER, K_UP)):
            break


main()
