import ti_draw
import random
import time
import ti_graphics
from ti_system import *

# Dimensions
SCREEN_WIDTH  = 321
SCREEN_HEIGHT = 211
CHAR_W = 10

# Board
TILE_SIZE  = 25
BOARD_SIZE = TILE_SIZE * 8
BOARD_X    = 5      # board sits on the left, text goes on the right
BOARD_Y    = (SCREEN_HEIGHT - BOARD_SIZE) // 2
PIECE_H    = 20     # height of the piece sprites (bases line up)

# Colors
BG_COLOR = (255, 255, 255) # White
BOARDER = (0, 0, 0) # Black
BOARD_COLOR   = (196, 164, 120) # Light color
BOARD_TILE = (130, 92, 60)    # Dark color
GRID_COLOR = BOARD_TILE         # Lines between squares
HIGHLIGHT = (255, 255, 0) # Yellow
RED_FONT = (255, 0, 0)   
BLUE_FONT = (0, 0, 255)

# Keyboard Codes
SCND_KEY = 21
DEL_KEY = 23
UP_KEY = 25
DOWN_KEY = 34
LEFT_KEY = 24
RIGHT_KEY = 26
STAT_KEY = 33
CLEAR_KEY = 45
ENTER_KEY = 105

# b_bishop.png: 18 x 20
b_bishop_palette = [0]
b_bishop_sprites = {0: [0, 268567555, 235144706, 302514693, 369754372, 202114818, 168691713, 135268353, 470811143, 135398913, 437388038, 101975555, 403965187, 370542082, 303564801, 135924738, 169740545, 35918338, 69734401]}

# b_king.png: 19 x 20
b_king_palette = [0]
b_king_sprites = {0: [0, 302121730, 335937798, 201853186, 135135753, 302908162, 537788936, 68158726, 470811910, 34735875, 437389059, 336855302, 303432453, 236456962, 102502145, 203295489, 69472515]}

# b_knight.png: 18 x 20
b_knight_palette = [0]
b_knight_sprites = {0: [0, 235144711, 201721862, 168299013, 134875908, 101453059, 68161025, 68289793, 303171335, 101974529, 236325125, 169347844, 135924739, 35918338, 69734401]}

# b_pawn.png: 18 x 20
b_pawn_palette = [0]
b_pawn_sprites = {0: [0, 268698638, 235275781, 201852931, 202508290, 135531521, 236324353, 236455172, 404357379, 203163650, 169740801, 35918338, 69734401]}

# b_queen.png: 23 x 20
b_queen_palette = [0]
b_queen_sprites = {0: [0, 268698371, 470024963, 67502851, 671482627, 34079745, 772276481, 135135491, 302907913, 470680073, 672006404, 101712641, 638583553, 168952324, 605160194, 370409734, 437519110, 236326146, 203033858, 236849921, 136581379]}

# b_rook.png: 18 x 20
b_rook_palette = [0]
b_rook_sprites = {0: [0, 134481160, 369362184, 101058055, 537264391, 303040514, 169085441, 202770437, 169478659, 102501890, 35918338, 69734401]}

# w_bishop.png: 18 x 20
w_bishop_palette = [16777215]
w_bishop_sprites = {0: [0, 268567555, 235144706, 302514693, 369754372, 202114818, 168691713, 135268353, 470811143, 135398913, 437388038, 101975555, 403965187, 370542082, 303564801, 135924738, 169740545, 35918338, 69734401]}

# w_king.png: 19 x 20
w_king_palette = [16777215]
w_king_sprites = {0: [0, 302121730, 335937798, 201853186, 135135753, 302908162, 537788936, 68158726, 470811910, 34735875, 437389059, 336855302, 303432453, 236456962, 102502145, 203295489, 69472515]}

# w_knight.png: 18 x 20
w_knight_palette = [16777215]
w_knight_sprites = {0: [0, 235144711, 201721862, 168299013, 134875908, 101453059, 68161025, 68289793, 303171335, 101974529, 236325125, 169347844, 135924739, 35918338, 69734401]}

# w_pawn.png: 18 x 20
w_pawn_palette = [16777215]
w_pawn_sprites = {0: [0, 268698638, 235275781, 201852931, 202508290, 135531521, 236324353, 236455172, 404357379, 203163650, 169740801, 35918338, 69734401]}

# w_queen.png: 23 x 20
w_queen_palette = [16777215]
w_queen_sprites = {0: [0, 268698371, 470024963, 67502851, 671482627, 34079745, 772276481, 135135491, 302907913, 470680073, 672006404, 101712641, 638583553, 168952324, 605160194, 370409734, 437519110, 236326146, 203033858, 236849921, 136581379]}

# w_rook.png: 18 x 20
w_rook_palette = [16777215]
w_rook_sprites = {0: [0, 134481160, 369362184, 101058055, 537264391, 303040514, 169085441, 202770437, 169478659, 102501890, 35918338, 69734401]}


def draw_bg(color=BG_COLOR):
    ti_draw.set_color(*color)
    ti_draw.fill_rect(-1, -1, SCREEN_WIDTH, SCREEN_HEIGHT)


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


def draw_sprite(x, y, prepared):
    for sprite_id in prepared:
        color, rectangles = prepared[sprite_id]
        ti_draw.set_color(*color)
        for px, py, w, h in rectangles:
            ti_draw.fill_rect(x + px - 2, y + py - 2, w + 1, h + 1)


def make_piece(palette, sprs):
    # Prepare a sprite once and work out the box it actually draws in,
    # so it can be centered no matter how much empty space it has
    prepared = prepare_sprite(palette, sprs)
    min_x = min_y = 999
    max_x = max_y = 0
    for color, rectangles in prepared.values():
        for px, py, w, h in rectangles:
            # The encoder stores x+1 / y+1, so the real pixel is px-1
            min_x = min(min_x, px - 1)
            min_y = min(min_y, py - 1)
            max_x = max(max_x, px - 1 + w)
            max_y = max(max_y, py - 1 + h)
    return (prepared, min_x, min_y, max_x - min_x, max_y - min_y)


def draw_piece(row, col, piece):
    # Center the piece left/right inside the square, and stand every
    # piece on the same bottom line so their bases line up. The inside
    # of a square is the TILE_SIZE - 1 pixels between its grid lines.
    prepared, min_x, min_y, w, h = piece
    inner = TILE_SIZE - 1
    x = BOARD_X + col * TILE_SIZE + 1 + (inner - w) // 2 - min_x
    bottom = BOARD_Y + row * TILE_SIZE + 1 + (inner - PIECE_H) // 2 + PIECE_H
    y = bottom - h - min_y
    draw_sprite(x, y, prepared)


# Row order for drawing a new board
DRAW_ORDER = [6, 7, 1, 0, 2, 3, 4, 5]


def draw_board():
    # One rectangle for the whole board in the light color
    ti_draw.set_color(*BOARD_COLOR)
    ti_draw.fill_rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)

    # Then the 32 dark tiles on top (top-left square is light)
    ti_draw.set_color(*BOARD_TILE)
    for row in range(8):
        for col in range((row + 1) % 2, 8, 2):
            ti_draw.fill_rect(BOARD_X + col * TILE_SIZE,
                              BOARD_Y + row * TILE_SIZE,
                              TILE_SIZE, TILE_SIZE)

    # Grid lines between squares in the dark tile color
    ti_draw.set_color(*GRID_COLOR)
    for i in range(1, 8):
        offset = i * TILE_SIZE
        ti_draw.draw_line(BOARD_X + offset, BOARD_Y,
                          BOARD_X + offset, BOARD_Y + BOARD_SIZE)
        ti_draw.draw_line(BOARD_X, BOARD_Y + offset,
                          BOARD_X + BOARD_SIZE, BOARD_Y + offset)

    draw_outer_border()


def draw_outer_border():
    # Black border around the whole board only
    left, top = BOARD_X, BOARD_Y
    right, bottom = BOARD_X + BOARD_SIZE, BOARD_Y + BOARD_SIZE
    ti_draw.set_color(*BOARDER)
    ti_draw.draw_line(left, top, right, top)
    ti_draw.draw_line(left, bottom, right, bottom)
    ti_draw.draw_line(left, top, left, bottom)
    ti_draw.draw_line(right, top, right, bottom)


def draw_tile(row, col):
    # Fill one square with its light/dark color
    if (row + col) % 2 == 0:
        ti_draw.set_color(*BOARD_COLOR)
    else:
        ti_draw.set_color(*BOARD_TILE)
    ti_draw.fill_rect(BOARD_X + col * TILE_SIZE,
                      BOARD_Y + row * TILE_SIZE,
                      TILE_SIZE, TILE_SIZE)


def square_edges(row, col):
    # The 4 border lines of one square, each with the color it has
    # normally: black on the board's outer edge, grid color inside
    x0 = BOARD_X + col * TILE_SIZE
    y0 = BOARD_Y + row * TILE_SIZE
    x1 = x0 + TILE_SIZE
    y1 = y0 + TILE_SIZE
    return [
        ((x0, y0, x1, y0), row == 0),   # top
        ((x0, y1, x1, y1), row == 7),   # bottom
        ((x0, y0, x0, y1), col == 0),   # left
        ((x1, y0, x1, y1), col == 7),   # right
    ]


def show_cursor(row, col, color=HIGHLIGHT):
    ti_draw.set_color(*color)
    for line, _ in square_edges(row, col):
        ti_draw.draw_line(*line)


def hide_cursor(row, col):
    # Redraw the exact same 4 lines in their normal colors, so every
    # blue pixel gets covered. Grid lines first, then black on top so
    # the board's outer border wins at the corners.
    edges = square_edges(row, col)
    ti_draw.set_color(*GRID_COLOR)
    for line, outer in edges:
        if not outer:
            ti_draw.draw_line(*line)
    ti_draw.set_color(*BOARDER)
    for line, outer in edges:
        if outer:
            ti_draw.draw_line(*line)


PIECES = {
    "bP": make_piece(b_pawn_palette,   b_pawn_sprites),
    "bR": make_piece(b_rook_palette,   b_rook_sprites),
    "bN": make_piece(b_knight_palette, b_knight_sprites),
    "bB": make_piece(b_bishop_palette, b_bishop_sprites),
    "bQ": make_piece(b_queen_palette,  b_queen_sprites),
    "bK": make_piece(b_king_palette,   b_king_sprites),
    "wP": make_piece(w_pawn_palette,   w_pawn_sprites),
    "wR": make_piece(w_rook_palette,   w_rook_sprites),
    "wN": make_piece(w_knight_palette, w_knight_sprites),
    "wB": make_piece(w_bishop_palette, w_bishop_sprites),
    "wQ": make_piece(w_queen_palette,  w_queen_sprites),
    "wK": make_piece(w_king_palette,   w_king_sprites),
}


def new_board():
    # board[sq], sq = row * 8 + col, row 0 is the top (black's back rank)
    b = [""] * 64
    b[0:8] = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"]
    b[8:16] = ["bP"] * 8
    b[48:56] = ["wP"] * 8
    b[56:64] = ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
    return b


# ---------- Chess rules ----------

VAL = {"P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 20000}
KNIGHT = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
KING   = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
STRAIGHT = ((-1, 0), (1, 0), (0, -1), (0, 1))
DIAGONAL = ((-1, -1), (-1, 1), (1, -1), (1, 1))
SLIDES = {"R": STRAIGHT, "B": DIAGONAL, "Q": STRAIGHT + DIAGONAL}


def other(side):
    return "b" if side == "w" else "w"


def attacked(b, sq, by):
    # True if side `by` attacks square sq
    r, c = divmod(sq, 8)
    # Pawns: a white pawn attacks upward, so it sits one row below
    pr = r + 1 if by == "w" else r - 1
    if 0 <= pr < 8:
        for dc in (-1, 1):
            if 0 <= c + dc < 8 and b[pr * 8 + c + dc] == by + "P":
                return True
    for dr, dc in KNIGHT:
        r2, c2 = r + dr, c + dc
        if 0 <= r2 < 8 and 0 <= c2 < 8 and b[r2 * 8 + c2] == by + "N":
            return True
    for dr, dc in KING:
        r2, c2 = r + dr, c + dc
        if 0 <= r2 < 8 and 0 <= c2 < 8 and b[r2 * 8 + c2] == by + "K":
            return True
    for dirs, kinds in ((STRAIGHT, "RQ"), (DIAGONAL, "BQ")):
        for dr, dc in dirs:
            r2, c2 = r + dr, c + dc
            while 0 <= r2 < 8 and 0 <= c2 < 8:
                p = b[r2 * 8 + c2]
                if p:
                    if p[0] == by and p[1] in kinds:
                        return True
                    break
                r2 += dr
                c2 += dc
    return False


def gen_moves(b, side, ep, cs):
    # Every move the pieces can make, ignoring whether it leaves your
    # own king in check (legal_moves filters those out)
    moves = []
    fwd = -1 if side == "w" else 1
    start = 6 if side == "w" else 1
    for sq in range(64):
        p = b[sq]
        if not p or p[0] != side:
            continue
        t = p[1]
        r, c = divmod(sq, 8)
        if t == "P":
            s2 = sq + 8 * fwd
            if not b[s2]:
                moves.append((sq, s2))
                if r == start and not b[s2 + 8 * fwd]:
                    moves.append((sq, s2 + 8 * fwd))
            for dc in (-1, 1):
                if 0 <= c + dc < 8:
                    s3 = s2 + dc
                    q = b[s3]
                    if (q and q[0] != side) or s3 == ep:
                        moves.append((sq, s3))
        elif t == "N" or t == "K":
            for dr, dc in (KNIGHT if t == "N" else KING):
                r2, c2 = r + dr, c + dc
                if 0 <= r2 < 8 and 0 <= c2 < 8:
                    s2 = r2 * 8 + c2
                    q = b[s2]
                    if not q or q[0] != side:
                        moves.append((sq, s2))
            if t == "K" and cs:
                ks, qs = ("K", "Q") if side == "w" else ("k", "q")
                opp = other(side)
                if ks in cs and not b[sq + 1] and not b[sq + 2] \
                        and b[sq + 3] == side + "R" \
                        and not attacked(b, sq, opp) \
                        and not attacked(b, sq + 1, opp):
                    moves.append((sq, sq + 2))
                if qs in cs and not b[sq - 1] and not b[sq - 2] \
                        and not b[sq - 3] and b[sq - 4] == side + "R" \
                        and not attacked(b, sq, opp) \
                        and not attacked(b, sq - 1, opp):
                    moves.append((sq, sq - 2))
        else:
            for dr, dc in SLIDES[t]:
                r2, c2 = r + dr, c + dc
                while 0 <= r2 < 8 and 0 <= c2 < 8:
                    s2 = r2 * 8 + c2
                    q = b[s2]
                    if q:
                        if q[0] != side:
                            moves.append((sq, s2))
                        break
                    moves.append((sq, s2))
                    r2 += dr
                    c2 += dc
    return moves


# Castling rights lost when a piece moves from or to these squares
CASTLE_SQ = ((60, "KQ"), (63, "K"), (56, "Q"), (4, "kq"), (7, "k"), (0, "q"))


def make_move(b, m, ep, cs):
    # Returns (new board, new en passant square, new castling rights)
    f, t = m
    nb = b[:]
    p = nb[f]
    nb[t] = p
    nb[f] = ""
    nep = -1
    if p[1] == "P":
        if t == ep:                         # en passant: remove the pawn
            nb[t + (8 if p[0] == "w" else -8)] = ""
        if abs(t - f) == 16:
            nep = (f + t) // 2
        if t < 8 or t >= 56:                # promotion: always a queen
            nb[t] = p[0] + "Q"
    elif p[1] == "K" and abs(t - f) == 2:   # castling: move the rook too
        if t > f:
            nb[f + 1] = nb[f + 3]
            nb[f + 3] = ""
        else:
            nb[f - 1] = nb[f - 4]
            nb[f - 4] = ""
    if cs:
        for sq, lose in CASTLE_SQ:
            if f == sq or t == sq:
                for ch in lose:
                    cs = cs.replace(ch, "")
    return nb, nep, cs


def in_check(b, side):
    return attacked(b, b.index(side + "K"), other(side))


def legal_moves(b, side, ep, cs):
    legal = []
    for m in gen_moves(b, side, ep, cs):
        nb = make_move(b, m, ep, cs)[0]
        if not in_check(nb, side):
            legal.append(m)
    return legal


def no_mating_material(b):
    # True when nobody can checkmate: king vs king, king and one bishop
    # or knight vs king, or king and bishop vs king and bishop with both
    # bishops on the same square color.
    minors = []
    for sq in range(64):
        p = b[sq]
        if p and p[1] != "K":
            if p[1] != "B" and p[1] != "N":
                return False
            minors.append((p, sq))
    if len(minors) <= 1:
        return True
    if len(minors) == 2:
        (p1, s1), (p2, s2) = minors
        if p1[1] == "B" and p2[1] == "B" and p1[0] != p2[0]:
            return (s1 // 8 + s1 % 8) % 2 == (s2 // 8 + s2 % 8) % 2
    return False


def position_key(b, side, ep, cs):
    # Same key = same position (pieces, side to move, en passant, castling)
    return ",".join(b) + side + cs + str(ep)


# ---------- CPU player ----------

# How close each square is to the middle: 0 on the edge, 3 in the center
CENTER = [3 - max(abs(2 * (s // 8) - 7), abs(2 * (s % 8) - 7)) // 2
          for s in range(64)]
PST_MUL = {"N": 5, "B": 3, "R": 0, "Q": 1}
# King center bonus per side. Set before every CPU move by set_phase():
# middlegame -4 (hide), endgame +4 (walk to the middle and help),
# and when one side is clearly winning the loser's king is pushed to the edge.
KMUL = {"w": -4, "b": -4}
MOPUP = [None]          # side that is winning the endgame, or None
ENDGAME = 2600          # pieces (no pawns/kings) worth less than this = endgame
MOPUP_LEAD = 300        # material lead needed to start hunting the king
MOPUP_W = 6             # bonus per square the kings get closer
PIECES_LEFT = {"w": 0, "b": 0}   # value of each side's pieces (no pawns/kings)


def set_phase(b):
    # Decide once per CPU move whether this is an endgame, and if so
    # who should chase the other king
    pieces = 0
    mat = {"w": 0, "b": 0}
    PIECES_LEFT["w"] = PIECES_LEFT["b"] = 0
    for p in b:
        if p and p[1] != "K":
            mat[p[0]] += VAL[p[1]]
            if p[1] != "P":
                pieces += VAL[p[1]]
                PIECES_LEFT[p[0]] += VAL[p[1]]
    MOPUP[0] = None
    if pieces > ENDGAME:
        KMUL["w"] = KMUL["b"] = -4
        return
    KMUL["w"] = KMUL["b"] = 4
    diff = mat["w"] - mat["b"]
    if abs(diff) >= MOPUP_LEAD:
        win = "w" if diff > 0 else "b"
        MOPUP[0] = win
        KMUL[win] = 2
        KMUL[other(win)] = 10


def pst(p, sq):
    # Small position bonus: knights and bishops like the center, pawns
    # like to advance, the king hides (middlegame) or centralizes (endgame)
    if p[1] == "P":
        rows_left = sq // 8 if p[0] == "w" else 7 - sq // 8
        c = sq % 8
        return (6 - rows_left) * 8 + (CENTER[sq] * 4 if 2 <= c <= 5 else 0)
    if p[1] == "K":
        return CENTER[sq] * KMUL[p[0]]
    return CENTER[sq] * PST_MUL[p[1]]


def dist(a, b):
    return abs(a // 8 - b // 8) + abs(a % 8 - b % 8)


def evaluate(b, side):
    # Full score of a position from side's point of view (material + position)
    s = 0
    for sq in range(64):
        p = b[sq]
        if p and p[1] != "K":
            v = VAL[p[1]] + pst(p, sq)
            s += v if p[0] == side else -v
        elif p:
            s += pst(p, sq) if p[0] == side else -pst(p, sq)
    return s


def gain(b, m, ep):
    # How much a move improves the mover's score (material + position)
    f, t = m
    p = b[f]
    q = b[t]
    g = -pst(p, f)
    if p[1] == "P" and (t < 8 or t >= 56):
        g += VAL["Q"] - VAL["P"] + pst(p[0] + "Q", t)
    else:
        g += pst(p, t)
    if q:
        g += VAL[q[1]] + pst(q, t)
    elif p[1] == "P" and t == ep:
        g += VAL["P"] + pst(other(p[0]) + "P", t + (8 if p[0] == "w" else -8))
    if p[1] == "K" and MOPUP[0]:
        # Winning side wants the kings close, losing side wants them apart
        ek = b.index(other(p[0]) + "K")
        d = (dist(f, ek) - dist(t, ek)) * MOPUP_W
        g += d if p[0] == MOPUP[0] else -d
    return g


WIN = 50000
DEPTH = (1, 2, 3)          # moves looked ahead for Easy, Normal, Hard
NOISE = (150, 30, 5)       # random wobble added to each move's score
DRAW = {"w": 0, "b": 0}    # what a draw is worth to each side (set by cpu_move)


def search(b, side, ep, cs, depth, alpha, beta, score):
    # Negamax with alpha-beta. score is from `side`'s point of view.
    # Uses unfiltered moves: a move that leaves the king hanging is
    # caught one level deeper, when the king gets taken.
    moves = gen_moves(b, side, ep, cs)
    if not moves:
        return 0
    if depth == 1:
        # Last level: just the best gain. Stop as soon as one move is
        # good enough that the level above will ignore this line.
        best = -WIN * 2
        for m in moves:
            q = b[m[1]]
            if q and q[1] == "K":
                return WIN + depth      # we can take the king
            v = score + gain(b, m, ep)
            if v > best:
                best = v
                if best >= beta:
                    return best
        return best
    scored = []
    for m in moves:
        q = b[m[1]]
        if q and q[1] == "K":
            return WIN + depth          # we can take the king
        scored.append((gain(b, m, ep), m))
    scored.sort(reverse=True)           # best-looking moves first
    opp = other(side)
    best = -WIN * 2
    for g, m in scored:
        nb, nep, ncs = make_move(b, m, ep, cs)
        v = -search(nb, opp, nep, ncs, depth - 1, -beta, -alpha, -(score + g))
        if v > best:
            best = v
            if v > alpha:
                alpha = v
                if alpha >= beta:
                    break
    if best <= -WIN and not in_check(b, side):
        # Every move loses the king, but we're not in check: that's
        # stalemate (a draw), not checkmate
        return DRAW[side]
    return best


def cpu_move(b, side, ep, cs, legal, level, seen):
    depth = DEPTH[level]
    noise = NOISE[level]
    opp = other(side)
    set_phase(b)
    # Stalemate only really happens when the other side has (almost) no
    # pieces left, so only then check every move for mate/stalemate
    check_end = PIECES_LEFT[opp] <= VAL["R"]
    # Scores are measured from the current position, so a draw (worth 0)
    # is worth -base: bad when ahead (avoid repeating/stalemating), good
    # when behind (happy to take a draw)
    draw_v = -evaluate(b, side)
    DRAW[side] = draw_v
    DRAW[opp] = -draw_v
    # Try the best-looking moves first so a good score is found early
    scored = sorted([(gain(b, m, ep), m) for m in legal], reverse=True)
    best, best_m = None, legal[0]
    for g, m in scored:
        nb, nep, ncs = make_move(b, m, ep, cs)
        if position_key(nb, opp, nep, ncs) in seen:
            v = draw_v                      # repeats a position
        elif depth == 1:
            v = g
        elif check_end and not legal_moves(nb, opp, nep, ncs):
            # Opponent has no moves: checkmate or stalemate
            v = WIN * 2 if in_check(nb, opp) else draw_v
        else:
            # Only care whether this move can beat the best so far
            # (minus the noise, which could still lift it to the top).
            # Moves that can't are cut off early instead of searched fully.
            alpha = -WIN * 2 if best is None else best - noise
            v = -search(nb, opp, nep, ncs, depth - 1, -WIN * 2, -alpha, -g)
        v += random.randint(0, noise)
        if best is None or v > best:
            best, best_m = v, m
    return best_m


# ---------- Title screen ----------

TEXT_COLOR  = (0, 0, 0)          # Black
TITLE_COLOR   = (220, 0, 0)       # Red
BRACKET_COLOR = TITLE_COLOR
TITLE_BG      = BOARD_COLOR       # title screen background

# Big title letters, 5 x 7 pixel grid, drawn TITLE_SCALE times bigger
TITLE_SCALE = 6
TITLE_FONT = {
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "h": ["#....", "#....", "#.##.", "##..#", "#...#", "#...#", "#...#"],
    "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    "s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
}

TITLE_Y   = 16                   # top of the big "Chess"
HEAD_Y    = 92                   # "Select difficulty:" / "Select your color:"
MENU_Y    = 124                  # first menu option
MENU_STEP = 24                   # space between lines
MENU      = ["Easy", "Normal", "Hard"]
COLORS    = ["White", "Black", "Demo"]

_last_key = [0]


def read_key():
    while True:
        k = get_key(0)
        if k != _last_key[0]:
            _last_key[0] = k
            if k:
                return k


def fill_box(x, y, w, h):
    # fill_rect draws 1 px short, so shift and grow it (same as draw_sprite)
    ti_draw.fill_rect(x - 1, y - 1, w + 1, h + 1)


def draw_big_text(text, y, color):
    # Centered block letters. Each row of a letter is drawn as runs of
    # filled pixels, so a letter takes only a handful of rectangles.
    s = TITLE_SCALE
    x = (SCREEN_WIDTH - (len(text) * 6 - 1) * s) // 2
    ti_draw.set_color(*color)
    for ch in text:
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
    ti_draw.set_color(*color)
    ti_draw.draw_text(SCREEN_WIDTH // 2 - len(text) * CHAR_W // 2, y, text)


def draw_brackets(options, i, color):
    # Draw "[" and "]" around option i. The brackets sit at the same x
    # for every option, sized to the longest one, so they line up like
    # [  Easy  ] / [ Normal ]. Drawing them again in the background
    # color erases them.
    longest = max(len(t) for t in options)
    x = SCREEN_WIDTH // 2 - longest * CHAR_W // 2
    y = MENU_Y + i * MENU_STEP
    ti_draw.set_color(*color)
    ti_draw.draw_text(x - CHAR_W - 6, y, "[")
    ti_draw.draw_text(x + longest * CHAR_W + 6, y, "]")


def clear_menu():
    ti_draw.set_color(*TITLE_BG)
    fill_box(0, HEAD_Y - 22, SCREEN_WIDTH, SCREEN_HEIGHT - HEAD_Y + 22)


def run_menu(heading, options, sel=0):
    # Show a menu under the title, starting on option sel. Returns the
    # picked index, or None if CLEAR is pressed. The menu is cleared
    # before returning.
    draw_text_centered(HEAD_Y, heading, TEXT_COLOR)
    for i, option in enumerate(options):
        draw_text_centered(MENU_Y + i * MENU_STEP, option, TEXT_COLOR)
    draw_brackets(options, sel, BRACKET_COLOR)
    while True:
        key = read_key()
        if key == CLEAR_KEY or key == ENTER_KEY:
            clear_menu()
            return sel if key == ENTER_KEY else None

        new_sel = sel
        if key == UP_KEY and sel > 0:
            new_sel -= 1
        elif key == DOWN_KEY and sel < len(options) - 1:
            new_sel += 1

        if new_sel != sel:
            draw_brackets(options, sel, TITLE_BG)        # erase old brackets
            sel = new_sel
            draw_brackets(options, sel, BRACKET_COLOR)   # draw new brackets


def title_screen():
    # Returns (level, color): level 0 = Easy, 1 = Normal, 2 = Hard and
    # color "w", "b", or "c" (CPU vs CPU: you just watch). Returns None if CLEAR is pressed on the first menu.
    # CLEAR on the color menu goes back to the difficulty menu.
    draw_bg(TITLE_BG)
    draw_big_text("Chess", TITLE_Y, TITLE_COLOR)
    while True:
        level = run_menu("Select difficulty:", MENU, 1)   # Normal picked
        if level is None:
            return None
        color = run_menu("Select your color:", COLORS)
        if color is not None:
            return level, "wbc"[color]


# ---------- Game ----------

SELECT_COLOR = (0, 0, 255)        # Blue border on the picked piece
CHECK_COLOR  = (220, 0, 0)        # Red "Check" text
# Message box to the right of the board, same height as the board
BOX_L = BOARD_X + BOARD_SIZE + 6
BOX_R = SCREEN_WIDTH - 6
BOX_T = BOARD_Y
BOX_B = BOARD_Y + BOARD_SIZE
PANEL_BG = BOARD_COLOR            # inside of the message box
SMALL_FONT = 0                    # ti_graphics.setFont: 0 = small, 1 = medium
NORMAL_FONT = 1
SMALL_CHAR_W = 8                  # small font: about 40 letters across 320 px
SMALL_SHIFT = 16                  # nudge small text: minus = left, plus = right
MOVE_LEN = 9                      # "W: e2, e4" - move lines are padded to this
LINE_H = 22                       # space between normal lines in the box
SMALL_H = 17                      # space between small-font lines
STATUS_Y = BOX_T + 25             # "Your move" / "Thinking" / "Checkmate"
CHECK_Y = STATUS_Y + LINE_H       # "Check!" / "You win!"
MOVES_Y = CHECK_Y + LINE_H + 10   # the two move lines (YOU / CPU)
HELP = ["[enter/clear]", "[del] Undo", "[2nd] Quit"]   # Easy / Normal
HELP_HARD = ["", "[enter/clear]", "[2nd] Quit"]           # Hard: no undo
HELP_WATCH = ["", "", "[2nd] Quit"]                       # CPU vs CPU
HELP_END = ["", "[stat] Score", "[enter] Menu"]           # game over
UNDO_LEVELS = (0, 1)              # undo only on Easy and Normal
MAX_UNDO = 10                     # saved turns kept for undo (limits memory)
HELP_Y = BOX_B - 8 - (len(HELP) - 1) * SMALL_H  # key help at the bottom
ARROWS = {UP_KEY: (-1, 0), DOWN_KEY: (1, 0), LEFT_KEY: (0, -1), RIGHT_KEY: (0, 1)}
flipped = False                   # True when you play black (board upside down)


def view(sq):
    # Board square -> (row, col) on screen. When you play black the
    # board is turned around so your pieces are at the bottom.
    r, c = divmod(sq, 8)
    return (7 - r, 7 - c) if flipped else (r, c)


def show_sq(sq, color=HIGHLIGHT):
    r, c = view(sq)
    show_cursor(r, c, color)


def hide_sq(sq):
    r, c = view(sq)
    hide_cursor(r, c)


def sq_name(sq):
    return "abcdefgh"[sq % 8] + str(8 - sq // 8)


def san(b, m, legal):
    # Standard algebraic notation for move m, played from board b:
    # "e4", "exd5", "Nbd7", "R1e2", "O-O", "e8=Q". The "+" or "#" is
    # added later, once the next position's legal moves are known.
    f, t = m
    p = b[f][1]
    if p == "K" and abs(t - f) == 2:
        return "O-O" if t > f else "O-O-O"
    dest = sq_name(t)
    if p == "P":
        s = dest
        if f % 8 != t % 8:               # pawns only change file to capture
            s = "abcdefgh"[f % 8] + "x" + dest
        if t < 8 or t >= 56:
            s += "=Q"
        return s
    # Another piece of the same kind that can also reach t: add the
    # file, or the rank if they share a file, or both if needed
    same_file = same_rank = clash = False
    for f2, t2 in legal:
        if t2 == t and f2 != f and b[f2] == b[f]:
            clash = True
            if f2 % 8 == f % 8:
                same_file = True
            if f2 // 8 == f // 8:
                same_rank = True
    s = p
    if clash:
        name = sq_name(f)
        if not same_file:
            s += name[0]
        elif not same_rank:
            s += name[1]
        else:
            s += name
    if b[t]:
        s += "x"
    return s + dest


def draw_box():
    # Message area filled with the board color, with a black border
    ti_draw.set_color(*PANEL_BG)
    fill_box(BOX_L + 1, BOX_T + 1, BOX_R - BOX_L - 1, BOX_B - BOX_T - 1)
    ti_draw.set_color(*BOARDER)
    ti_draw.draw_line(BOX_L, BOX_T, BOX_R, BOX_T)
    ti_draw.draw_line(BOX_L, BOX_B, BOX_R, BOX_B)
    ti_draw.draw_line(BOX_L, BOX_T, BOX_L, BOX_B)
    ti_draw.draw_line(BOX_R, BOX_T, BOX_R, BOX_B)


def text_width(text, small):
    # Pixel width of text in the font that is set now. Small letters
    # are not all the same width, so measure with string_size() when
    # the calculator has it; otherwise guess from the letter count.
    for mod in (ti_draw, ti_graphics):
        f = getattr(mod, "string_size", None)
        if f:
            s = f(text)
            return s if isinstance(s, int) else s[0]
    return len(text) * (SMALL_CHAR_W if small else CHAR_W)


def move_text(who, text=""):
    # "W: e2," -> "W: e2,   " : always MOVE_LEN characters, so the
    # centered line stays put while the move is typed in
    s = who + ": " + text
    return s + " " * (MOVE_LEN - len(s))


KEY_COLOR = BLUE_FONT          # key names inside "[...]"


def draw_keys(x, y, text, color, small):
    # Draw text with the key names inside "[...]" in KEY_COLOR
    ti_draw.set_color(*color)
    ti_draw.draw_text(x, y, text)
    runs = []                        # (start, end) of each key name
    inside = False
    start = -1
    for i in range(len(text) + 1):
        ch = text[i] if i < len(text) else "]"
        key = inside and ch not in "[]/"
        if ch == "[":
            inside = True
        elif ch == "]":
            inside = False
        if key and start < 0:
            start = i
        elif not key and start >= 0:
            runs.append((start, i))
            start = -1
    for start, end in reversed(runs):
        ti_draw.set_color(*KEY_COLOR)
        ti_draw.draw_text(x, y, text[:end])
        ti_draw.set_color(*color)
        if start:
            ti_draw.draw_text(x, y, text[:start])


def text_line(y, text, color=TEXT_COLOR, small=False):
    # Clear one line of the message box and write text on it, centered
    # in the box. Only that line is cleared, so the rest of the box
    # (and its border) stays.
    h = SMALL_H if small else LINE_H
    ti_draw.set_color(*PANEL_BG)
    fill_box(BOX_L + 1, y - h + 5, BOX_R - BOX_L - 1, h)
    if text:
        if small:
            ti_graphics.setFont(SMALL_FONT)
        x = BOX_L + 1 + (BOX_R - BOX_L - 1 - text_width(text, small)) // 2
        if small:
            x += SMALL_SHIFT
        draw_keys(x, y, text, color, small)
        if small:
            ti_graphics.setFont(NORMAL_FONT)   # always back to medium


def draw_help(lines):
    # Key help at the bottom of the box, in the small font. The whole
    # help area is cleared first so no old letters are left behind.
    top = HELP_Y - SMALL_H + 1
    ti_draw.set_color(*PANEL_BG)
    fill_box(BOX_L + 1, top, BOX_R - BOX_L - 1, BOX_B - top)
    for i in range(len(lines)):
        if lines[i]:
            text_line(HELP_Y + i * SMALL_H, lines[i], TEXT_COLOR, True)


def draw_all_pieces(b):
    for row in DRAW_ORDER:
        for col in range(8):
            sq = row * 8 + col
            if b[sq]:
                r, c = view(sq)
                draw_piece(r, c, PIECES[b[sq]])


def redraw_square(b, sq):
    r, c = view(sq)
    draw_tile(r, c)
    if b[sq]:
        draw_piece(r, c, PIECES[b[sq]])
    hide_cursor(r, c)               # put the square's normal edges back


def move_cursor_to(old, new, sel):
    hide_sq(old)
    if sel is not None:
        show_sq(sel, SELECT_COLOR)  # fix the edge it shares with old
    show_sq(new)


def jump_target(cur, targets, dr, dc):
    # The nearest target in the arrow's direction (on screen), or cur
    r, c = view(cur)
    best, best_score = cur, None
    for t in targets:
        tr, tc = view(t)
        ahead = (tr - r) * dr + (tc - c) * dc
        if ahead <= 0:
            continue
        sideways = abs((tr - r) * dc) + abs((tc - c) * dr)
        score = ahead + 2 * sideways
        if best_score is None or score < best_score:
            best, best_score = t, score
    return best


def player_move(b, legal, cur, you_y, you_tag, can_undo):
    # Yellow cursor moves freely. ENTER on your piece outlines it in
    # blue, then the arrows jump only between its legal squares.
    # ENTER moves there, CLEAR unselects, DEL undoes (when can_undo),
    # 2ND quits.
    # Your move line (at you_y) follows the cursor: "W: e2," and, once a
    # piece is picked, "W: e2, e4". Returns (move, cursor), (None,
    # cursor) for undo, or None to quit.
    sel = None
    targets = []
    shown = [None]

    def track():
        if sel is None:
            text = move_text(you_tag, sq_name(cur) + ",")
        else:
            text = move_text(you_tag, sq_name(sel) + ", " + sq_name(cur))
        if text != shown[0]:
            shown[0] = text
            text_line(you_y, text, BOARD_TILE)

    show_sq(cur)
    track()
    while True:
        key = read_key()
        if key in ARROWS:
            dr, dc = ARROWS[key]
            if sel is None:
                r, c = view(cur)
                r, c = r + dr, c + dc
                new = cur
                if 0 <= r < 8 and 0 <= c < 8:
                    new = (7 - r) * 8 + (7 - c) if flipped else r * 8 + c
            else:
                new = jump_target(cur, targets, dr, dc)
            if new != cur:
                move_cursor_to(cur, new, sel)
                cur = new
                track()
        elif key == ENTER_KEY:
            if sel is None:
                targets = [t for f, t in legal if f == cur]
                if targets:
                    sel = cur
                    # Start on the legal square closest to the piece
                    r, c = divmod(sel, 8)
                    new = min(targets, key=lambda t: abs(t // 8 - r) + abs(t % 8 - c))
                    show_sq(sel, SELECT_COLOR)
                    show_sq(new)
                    cur = new
                    track()
            else:
                hide_sq(cur)
                hide_sq(sel)
                return (sel, cur), cur
        elif key == CLEAR_KEY and sel is not None:
            hide_sq(cur)
            cur = sel                    # unselect: back on the piece
            sel = None
            show_sq(cur)
            track()
        elif key == SCND_KEY or (key == DEL_KEY and can_undo):
            hide_sq(cur)
            if sel is not None:
                hide_sq(sel)
            if key == DEL_KEY:
                return None, cur         # undo the last two moves
            return None                  # quit to the title screen


LOG_TOP = 24                      # y of the heading
LOG_Y = LOG_TOP + 26              # y of the first move line
LOG_H = 20                        # space between move lines
LOG_ROWS = 7                      # move lines that fit on one page
LOG_X = 10                        # left edge of the log text
LOG_BOTTOM = LOG_Y + (LOG_ROWS - 1) * LOG_H + 8   # line under the last move
LOG_HELP = "[up/down] Scroll   [clear] Menu"
LOG_COLS = (LOG_X, LOG_X + 45, LOG_X + 135)   # x of: number, white, black


def show_log(result, score, log):
    # Full-screen list of every move in algebraic notation, one turn per
    # line: "1. e4  e5". The score (1-0, 0-1, 1/2-1/2) follows the last
    # move. UP/DOWN scroll one line, LEFT/RIGHT one page, CLEAR (or 2ND)
    # goes back to the title screen.
    moves = log + [score]
    lines = []
    for i in range(0, len(moves), 2):
        lines.append([str(i // 2 + 1) + "."] + moves[i:i + 2])
    if len(log) % 2 == 0:
        lines[-1][0] = ""                # the score alone on its own line
    top = 0
    max_top = max(0, len(lines) - LOG_ROWS)

    # Heading, the two lines and the key help never change, so they
    # are drawn once. Scrolling only clears and redraws the moves
    # between the two lines.
    draw_bg()
    ti_draw.set_color(*BOARDER)
    ti_draw.draw_text(LOG_X, LOG_TOP, "Score Sheet - " + result)
    ti_draw.draw_line(LOG_X, LOG_TOP + 2, SCREEN_WIDTH - LOG_X, LOG_TOP + 2)
    ti_draw.draw_line(LOG_X, LOG_BOTTOM, SCREEN_WIDTH - LOG_X, LOG_BOTTOM)
    ti_graphics.setFont(SMALL_FONT)
    draw_keys(LOG_X, SCREEN_HEIGHT - 8, LOG_HELP, BOARDER, True)
    ti_graphics.setFont(NORMAL_FONT)

    while True:
        ti_draw.set_color(*BG_COLOR)
        fill_box(0, LOG_TOP + 3, SCREEN_WIDTH, LOG_BOTTOM - LOG_TOP - 3)
        ti_draw.set_color(*BOARD_TILE)
        for r in range(LOG_ROWS):
            if top + r < len(lines):
                cols = lines[top + r]
                for c in range(len(cols)):
                    ti_draw.draw_text(LOG_COLS[c], LOG_Y + r * LOG_H, cols[c])

        while True:
            key = read_key()
            new = top
            if key == UP_KEY:
                new = max(0, top - 1)
            elif key == DOWN_KEY:
                new = min(max_top, top + 1)
            elif key == LEFT_KEY:
                new = max(0, top - LOG_ROWS)
            elif key == RIGHT_KEY:
                new = min(max_top, top + LOG_ROWS)
            elif key == CLEAR_KEY or key == SCND_KEY:
                return
            if new != top:               # only redraw when it scrolled
                top = new
                break


CPU_PAUSE = 0.6                   # CPU vs CPU: seconds to wait between moves


def watch_pause():
    # CPU vs CPU: wait a moment so each move can be seen. Returns True
    # if 2ND was pressed (quit to the title screen).
    start = time.monotonic()
    while time.monotonic() - start < CPU_PAUSE:
        k = get_key(0)
        if k != _last_key[0]:
            _last_key[0] = k
            if k == SCND_KEY:
                return True
    return False


def run_game(level, you):
    # you = "w" or "b" for the side you play, "c" to watch CPU vs CPU
    global flipped
    flipped = you == "b"
    watch = you == "c"
    b = new_board()
    ep, cs = -1, "KQkq"
    draw_bg()
    draw_board()
    draw_box()
    draw_all_pieces(b)

    # Two move lines, in the order the players move
    first, second = MOVES_Y, MOVES_Y + LINE_H
    you_y, cpu_y = (second, first) if you == "b" else (first, second)
    you_tag, cpu_tag = ("B", "W") if you == "b" else ("W", "B")
    text_line(you_y, move_text(you_tag), BOARD_TILE)
    text_line(cpu_y, move_text(cpu_tag), BOARD_TILE)
    undo_ok = not watch and level in UNDO_LEVELS
    if watch:
        draw_help(HELP_WATCH)
    else:
        draw_help(HELP if undo_ok else HELP_HARD)

    side = "w"                       # white always moves first
    cur = 52 if you == "w" else 12   # cursor starts on your e-pawn
    clock = 0                        # half-moves since a capture or pawn move
    seen = {}                        # position key -> times it has happened
    log = []                         # every move so far, in algebraic notation
    last = None                      # CPU vs CPU: last move, outlined on the board
    history = []                     # undo: game state at each of your turns
    while True:
        if undo_ok and side == you:
            # Save the state before seen/log are touched this turn, so
            # going back to it replays this turn exactly
            # The log only grows (and its last line may get "+"/"#"), so
            # its length and last line are enough to put it back
            history.append((b, ep, cs, clock, dict(seen), len(log),
                            log[-1] if log else None))
            if len(history) > MAX_UNDO:
                history.pop(0)           # forget the oldest turn
        legal = legal_moves(b, side, ep, cs)
        check = in_check(b, side)
        key = position_key(b, side, ep, cs)
        seen[key] = seen.get(key, 0) + 1
        if log and check:
            log[-1] += "+" if legal else "#"   # the last move gave check

        draw = ""
        if not legal and not check:
            draw = "Stalemate"
        elif seen[key] >= 3:
            draw = "Repeat x3"           # same position 3 times
        elif clock >= 100:
            draw = "50 moves"            # 50 moves each, no capture/pawn move
        elif no_mating_material(b):
            draw = "Material"            # nobody has enough to checkmate

        if not legal or draw:
            if not legal and check:
                if watch:
                    who = other(side).upper() + " wins!"
                else:
                    who = "You lose" if side == you else "You win!"
                text_line(STATUS_Y, "Checkmate", CHECK_COLOR)
                text_line(CHECK_Y, who)
                result = other(side).upper() + ": Checkmate"   # the winner
                score = "0-1" if side == "w" else "1-0"
            else:
                text_line(STATUS_Y, "Draw")
                text_line(CHECK_Y, draw)
                result = draw
                score = "1/2-1/2"
            draw_help(HELP_END)
            while True:
                key = read_key()
                if key == STAT_KEY:
                    show_log(result, score, log)
                    return               # CLEAR in the log: title screen
                if key == ENTER_KEY or key == CLEAR_KEY or key == SCND_KEY:
                    return

        text_line(CHECK_Y, "Check!" if check else "", CHECK_COLOR)
        if side == you:
            text_line(STATUS_Y, "Your move")
            res = player_move(b, legal, cur, you_y, you_tag, len(history) > 1)
            if res is None:
                return                   # 2ND: back to the title screen
            m, cur = res
            if m is None:
                # Undo: take back the CPU's last move and your move
                # before it (the log loses both too)
                history.pop()            # this turn's state
                ob, ep, cs, clock, seen, n, last_line = history.pop()
                del log[n:]
                if n:
                    log[-1] = last_line
                for sq in range(64):
                    if ob[sq] != b[sq]:
                        redraw_square(ob, sq)
                b = ob
                text_line(you_y, move_text(you_tag), BOARD_TILE)
                text_line(cpu_y, move_text(cpu_tag), BOARD_TILE)
                continue
        else:
            # CPU's turn (in CPU vs CPU both sides: white on the top
            # line, black on the bottom)
            y, tag = (you_y, you_tag) if side == you_tag.lower() else (cpu_y, cpu_tag)
            text_line(STATUS_Y, "Thinking")
            text_line(y, move_text(tag), BOARD_TILE)
            m = cpu_move(b, side, ep, cs, legal, level, seen)
            text_line(y, move_text(tag, sq_name(m[0]) + ", " + sq_name(m[1])),
                      BOARD_TILE)

        if b[m[1]] or b[m[0]][1] == "P":
            # A capture or pawn move can't be undone: reset the 50-move
            # count, and older positions can never come back (frees memory)
            clock = 0
            seen = {}
        else:
            clock += 1

        log.append(san(b, m, legal))
        nb, ep, cs = make_move(b, m, ep, cs)
        for sq in range(64):         # redraw only the squares that changed
            if nb[sq] != b[sq]:
                redraw_square(nb, sq)
        b = nb
        if watch:
            # Outline the last move: blue where the piece came from,
            # yellow where it went. It stays up while the next CPU thinks.
            if last:
                hide_sq(last[0])
                hide_sq(last[1])
            show_sq(m[0], SELECT_COLOR)
            show_sq(m[1])
            last = m
        side = other(side)
        if watch and watch_pause():
            return                       # 2ND: back to the title screen


while True:
    choice = title_screen()
    if choice is None:
        break
    run_game(*choice)
