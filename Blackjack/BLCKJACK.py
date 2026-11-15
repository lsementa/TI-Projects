import ti_draw
import random
import ti_graphics
from ti_system import *

# Dimensions
SCREEN_WIDTH  = 321
SCREEN_HEIGHT = 211
BUTTON_HEIGHT = 22
CHAR_W = 10

# Colors
BG_COLOR   = (53, 101, 77)
MENU_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
GOLD_COLOR = (255, 215, 0)
RED_SUITE  = (255, 0, 0)
BLACK_SUITE = (0, 0, 0)

# Keys
CLEAR_KEY = 45
YEQ  = 11   # F1 - MAX / CLEAR bet
WIN  = 12   # F2 - $5
ZOOM = 13   # F3 - $20
TRCE = 14   # F4 - $100 / HIT
GRPH = 15   # F5 - DEAL / STAY

RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
SUITS = ["S","H","D","C"]

STARTING_BALANCE = 500

_menu = ["", "", "", "", ""]

card_palette = [16777215, 16645629, 0]

card_sprs = {0: [0, 100936449, 1543897345, 67513089, 67644729, 108669697], 1: [1, 1510342913], 2: [2, 100805377, 67371265, 1543766273, 33947962, 1577451834, 75104513, 1551499521, 108800769]}

card_back_palette = [16777215, 16645629, 15791094, 13294563, 91542, 0]

card_back_sprs = {0: [0, 100936449, 1543897345, 67513089, 67644673, 1409942785, 67765249, 1477182260, 67896116, 1416889601, 74712321, 74853634, 108669697], 1: [1, 1510342913], 2: [2, 201982209], 3: [3, 303177774], 4: [4, 235545345, 168568579, 168952878, 1376912174, 174991107, 242492161], 5: [5, 100805377, 67371265, 1543766273, 33947962, 1577451834, 75104513, 1551499521, 108800769]}

# Card layout
CARD_W       = 47
CARD_H       = 62
CARD_SPACING = CARD_W - 23   # overlap
DEALER_Y     = 20
PLAYER_Y     = 109

# Text y-positions for play screen
BAL_Y    = 19
D_VAL_Y  = 85
P_VAL_Y  = 174
STATUS_Y = 104   # center of gap between dealer and player

_dealer_cards = [[0, 0] for _ in range(10)]
_player_cards = [[0, 0] for _ in range(10)]


def shuffle(deck):
    for i in range(len(deck) - 1, 0, -1):
        j = random.randint(0, i)
        deck[i], deck[j] = deck[j], deck[i]


def hand_value(hand, count):
    total = 0
    aces  = 0
    for i in range(count):
        rank = hand[i] % 13
        if rank == 0:
            aces  += 1
            total += 1
        elif rank >= 10:
            total += 10
        else:
            total += rank + 1
    while aces > 0 and total <= 11:
        total += 10
        aces  -= 1
    return total


def draw_bg():
    ti_draw.set_color(*BG_COLOR)
    ti_draw.fill_rect(-1, -1, SCREEN_WIDTH, SCREEN_HEIGHT - BUTTON_HEIGHT)


def draw_value(x, y, card_value, color=BLACK_SUITE):
    ti_draw.set_color(*color)
    ti_graphics.setFont(0)
    # top-left corner
    ti_draw.draw_text(x + 3, y + 20, card_value)
    # bottom-right corner
    text_width = len(card_value) * 9
    ti_draw.draw_text(x + 47 - text_width, y + 62, card_value)
    ti_graphics.setFont(1)


def draw_diamond(x, y):
    ti_draw.set_color(*RED_SUITE)
    cx = x + 23
    cy = y + 31
    xs = [cx, cx + 7, cx, cx - 7, cx]
    ys = [cy - 9, cy, cy + 9, cy, cy - 9]
    ti_draw.fill_poly(xs, ys)


def draw_heart(x, y):
    ti_draw.set_color(*RED_SUITE)
    cx = x + 23
    cy = y + 31
    # Flat bump tops (cx-6→cx-9 and mirror) look rounder on low-res screens;
    # 4-segment lower curve gives a smooth path to the bottom point.
    xs = [cx,    cx-3,  cx-6,  cx-9,  cx-11, cx-12, cx-11, cx-9,  cx-6,  cx-3,  cx,    cx+3,  cx+6,  cx+9,  cx+11, cx+12, cx+11, cx+9,  cx+6,  cx+3,  cx]
    ys = [cy-5,  cy-9,  cy-11, cy-11, cy-8,  cy-4,  cy,    cy+4,  cy+7,  cy+9,  cy+11, cy+9,  cy+7,  cy+4,  cy,    cy-4,  cy-8,  cy-11, cy-11, cy-9,  cy-5]
    ti_draw.fill_poly(xs, ys)


def draw_club(x, y):
    ti_draw.set_color(*BLACK_SUITE)
    cx = x + 23
    cy = y + 31
    # Three lobes with radius 6 for visible overlap
    ti_draw.fill_circle(cx,     cy - 6, 6)
    ti_draw.fill_circle(cx - 6, cy + 2, 6)
    ti_draw.fill_circle(cx + 6, cy + 2, 6)
    # Solid rectangle to fill the gap between all three lobes
    ti_draw.fill_rect(cx - 4, cy - 2, 9, 7)
    # Narrow stem below
    xs = [cx - 4, cx + 4, cx + 2, cx - 2]
    ys = [cy + 7,  cy + 7, cy + 12, cy + 12]
    ti_draw.fill_poly(xs, ys)


def draw_spade(x, y):
    ti_draw.set_color(*BLACK_SUITE)
    cx = x + 23
    cy = y + 31
    # Exact y-mirror of the improved heart
    xs = [cx,    cx-3,  cx-6,  cx-9,  cx-11, cx-12, cx-11, cx-9,  cx-6,  cx-3,  cx,    cx+3,  cx+6,  cx+9,  cx+11, cx+12, cx+11, cx+9,  cx+6,  cx+3,  cx]
    ys = [cy+5,  cy+9,  cy+11, cy+11, cy+8,  cy+4,  cy,    cy-4,  cy-7,  cy-9,  cy-11, cy-9,  cy-7,  cy-4,  cy,    cy+4,  cy+8,  cy+11, cy+11, cy+9,  cy+5]
    ti_draw.fill_poly(xs, ys)
    # Stem sits in the notch between the bottom bumps
    xs = [cx - 4, cx + 4, cx + 2, cx - 2]
    ys = [cy + 10, cy + 10, cy + 15, cy + 15]
    ti_draw.fill_poly(xs, ys)


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


_card      = prepare_sprite(card_palette, card_sprs)
_card_back = prepare_sprite(card_back_palette, card_back_sprs)


def draw_sprite(x, y, prepared):
    for sprite_id in prepared:
        color, rectangles = prepared[sprite_id]
        ti_draw.set_color(*color)
        for px, py, w, h in rectangles:
            ti_draw.fill_rect(x + px - 2, y + py - 2, w + 1, h + 1)


def center_cards(user, num_cards):
    total_width = CARD_W + (num_cards - 1) * CARD_SPACING
    start_x     = (SCREEN_WIDTH - total_width) // 2
    for i in range(num_cards):
        cx = start_x + i * CARD_SPACING
        if user == 0:
            _player_cards[i][0] = cx
            _player_cards[i][1] = PLAYER_Y
        else:
            _dealer_cards[i][0] = cx
            _dealer_cards[i][1] = DEALER_Y


def _draw_suit(x, y, suit):
    if suit == 1:
        draw_heart(x, y)
    elif suit == 2:
        draw_diamond(x, y)
    elif suit == 3:
        draw_club(x, y)
    else:
        draw_spade(x, y)


def draw_card(x, y, card_index):
    draw_sprite(x, y, _card)
    suit  = card_index // 13
    rank  = card_index % 13
    color = RED_SUITE if suit in (1, 2) else BLACK_SUITE
    _draw_suit(x, y, suit)
    draw_value(x, y, RANKS[rank], color)


def draw_card_back_at(x, y):
    draw_sprite(x, y, _card_back)


def draw_hand(user, hand, count, hide_last=False):
    card_y = DEALER_Y if user == 1 else PLAYER_Y
    ti_draw.set_color(*BG_COLOR)
    ti_draw.fill_rect(0, card_y, SCREEN_WIDTH, CARD_H)
    cards = _dealer_cards if user == 1 else _player_cards
    for i in range(count):
        x, y = cards[i]
        if hide_last and i == count - 1:
            draw_card_back_at(x, y)
        else:
            draw_card(x, y, hand[i])


def draw_menu(labels):
    global _menu
    btn_y     = SCREEN_HEIGHT - BUTTON_HEIGHT - 2
    btn_width = SCREEN_WIDTH // 5

    for i, label in enumerate(labels):
        bw = SCREEN_WIDTH - i * btn_width - 2 if i == 4 else btn_width
        bx = i * btn_width

        ti_draw.set_color(*MENU_COLOR)
        ti_draw.fill_rect(bx, btn_y, bw, BUTTON_HEIGHT)
        ti_draw.set_color(*BG_COLOR)
        ti_draw.draw_rect(bx, btn_y, bw, BUTTON_HEIGHT)

        if label:
            tw = len(label) * CHAR_W
            tx = bx + (bw - tw) // 2
            ty = btn_y + (BUTTON_HEIGHT + BUTTON_HEIGHT) // 2
            ti_draw.set_color(*TEXT_COLOR)
            ti_draw.draw_text(tx, ty, label)

    _menu[:] = list(labels)


def update_menu_btn(i, prev_label, new_label):
    btn_y     = SCREEN_HEIGHT - BUTTON_HEIGHT - 2
    btn_width = SCREEN_WIDTH // 5
    bw = SCREEN_WIDTH - i * btn_width - 2 if i == 4 else btn_width
    bx = i * btn_width
    ty = btn_y + (BUTTON_HEIGHT + BUTTON_HEIGHT) // 2

    if prev_label:
        tw = len(prev_label) * CHAR_W
        tx = bx + (bw - tw) // 2
        ti_draw.set_color(*MENU_COLOR)
        ti_draw.draw_text(tx, ty, prev_label)

    if new_label:
        tw = len(new_label) * CHAR_W
        tx = bx + (bw - tw) // 2
        ti_draw.set_color(*TEXT_COLOR)
        ti_draw.draw_text(tx, ty, new_label)


def set_menu_btn(i, new_label):
    global _menu
    if _menu[i] != new_label:
        update_menu_btn(i, _menu[i], new_label)
        _menu[i] = new_label


def set_menu(labels):
    for i, label in enumerate(labels):
        set_menu_btn(i, label)


def lbl(x, y, text, color=TEXT_COLOR):
    ti_draw.set_color(*color)
    ti_draw.draw_text(x, y, text)


def erase_lbl(x, y, text, color=BG_COLOR):
    ti_draw.set_color(*color)
    ti_draw.draw_text(x, y, text)


def lbl_centered(y, text, color=TEXT_COLOR):
    x = max(0, (SCREEN_WIDTH - len(text) * CHAR_W) // 2)
    lbl(x, y, text, color)


def erase_lbl_centered(y, text):
    x = max(0, (SCREEN_WIDTH - len(text) * CHAR_W) // 2)
    erase_lbl(x, y, text)


def draw_bet_screen(balance, bet):
    draw_bg()
    set_menu(["CLEAR" if bet > 0 else "MAX", "+5", "+20", "+100", "DEAL"])
    lbl(4, 19, "$" + str(balance), GOLD_COLOR)
    lbl(4, 36, "Bet: $" + str(bet))


def draw_play_screen(balance, p_hand, p_count, d_hand, d_count, hide_dealer, status=""):
    draw_bg()
    set_menu(["", "", "", "HIT", "STAY"])
    lbl(4, 19, "$" + str(balance), GOLD_COLOR)

    center_cards(0, p_count)
    center_cards(1, d_count)
    draw_hand(0, p_hand, p_count)
    draw_hand(1, d_hand, d_count, hide_dealer)

    d_total = hand_value(d_hand, 1) if hide_dealer else hand_value(d_hand, d_count)
    lbl(4, D_VAL_Y, str(d_total))
    lbl(4, P_VAL_Y, str(hand_value(p_hand, p_count)))

    if status:
        lbl(4, STATUS_Y, status)


def update_dealer(prev_val, d_hand, d_count, hide_dealer):
    erase_lbl(4, D_VAL_Y, prev_val)
    center_cards(1, d_count)
    draw_hand(1, d_hand, d_count, hide_dealer)
    d_total = hand_value(d_hand, 1) if hide_dealer else hand_value(d_hand, d_count)
    new_val = str(d_total)
    lbl(4, D_VAL_Y, new_val)
    return new_val


def update_player(prev_val, p_hand, p_count):
    erase_lbl(4, P_VAL_Y, prev_val)
    center_cards(0, p_count)
    draw_hand(0, p_hand, p_count)
    new_val = str(hand_value(p_hand, p_count))
    lbl(4, P_VAL_Y, new_val)
    return new_val


def update_balance(prev_bal, balance):
    erase_lbl(4, BAL_Y, prev_bal)
    new_bal = "$" + str(balance)
    lbl(4, BAL_Y, new_bal, GOLD_COLOR)
    return new_bal


def update_status(prev_status, status):
    if prev_status:
        erase_lbl_centered(STATUS_Y, prev_status)
    if status:
        lbl_centered(STATUS_Y, status)
    return status


def play_round(balance, bet):
    deck = list(range(52)) * 2
    shuffle(deck)
    nxt = 0

    p_hand  = [0] * 10
    d_hand  = [0] * 10
    p_count = 0
    d_count = 0

    p_hand[p_count] = deck[nxt]; p_count += 1; nxt += 1
    d_hand[d_count] = deck[nxt]; d_count += 1; nxt += 1
    p_hand[p_count] = deck[nxt]; p_count += 1; nxt += 1
    d_hand[d_count] = deck[nxt]; d_count += 1; nxt += 1

    draw_play_screen(balance, p_hand, p_count, d_hand, d_count, True)

    d_val = str(hand_value(d_hand, 1))
    p_val = str(hand_value(p_hand, p_count))
    bal   = "$" + str(balance)
    sts   = ""

    skip_dealer = False

    while True:
        key = get_key(1)

        if key == TRCE:  # HIT
            p_hand[p_count] = deck[nxt]; p_count += 1; nxt += 1
            pv = hand_value(p_hand, p_count)

            p_val = update_player(p_val, p_hand, p_count)

            if pv > 21:
                skip_dealer = True
                d_val = update_dealer(d_val, d_hand, d_count, False)
                erase_lbl(4, D_VAL_Y, d_val)
                d_val = ""
                sts = update_status(sts, "Bust! Dealer wins.")
                break

            if p_count == 5:
                balance    += bet * 2
                skip_dealer = True
                d_val = update_dealer(d_val, d_hand, d_count, False)
                bal = update_balance(bal, balance)
                erase_lbl(4, D_VAL_Y, d_val)
                d_val = ""
                sts = update_status(sts, "5 Card Trick! You win!")
                break

        elif key == GRPH:  # STAY
            break

        elif key == CLEAR_KEY:
            return balance, True

    if not skip_dealer:
        pv = hand_value(p_hand, p_count)
        dv = hand_value(d_hand, d_count)
        d_val = update_dealer(d_val, d_hand, d_count, False)

        while dv < 17:
            d_hand[d_count] = deck[nxt]; d_count += 1; nxt += 1
            dv = hand_value(d_hand, d_count)
            d_val = update_dealer(d_val, d_hand, d_count, False)

        if dv > 21:
            balance += bet * 2
            outcome = "Dealer bust! You win!"
        elif dv > pv:
            outcome = "Dealer wins!"
        elif pv > dv:
            balance += bet * 2
            outcome = "You win!"
        else:
            balance += bet
            outcome = "Push."

        update_balance(bal, balance)
        erase_lbl(4, D_VAL_Y, d_val)
        d_val = ""
        sts = update_status(sts, outcome)

    set_menu_btn(3, "QUIT")
    set_menu_btn(4, "PLAY")

    while True:
        key = get_key(1)
        if key == GRPH:
            return balance, False
        if key == TRCE or key == CLEAR_KEY:
            return balance, True


def run_game():
    balance = STARTING_BALANCE
    bet     = 0

    draw_bg()
    draw_menu(["", "", "", "", ""])

    draw_bet_screen(balance, bet)
    prev_bet_text = "Bet: $0"

    while True:
        key = get_key(1)

        if key == CLEAR_KEY:
            break

        if key == YEQ:
            if bet > 0:
                bet = 0
            else:
                bet = balance

        elif key == WIN and balance - bet >= 5:
            bet += 5

        elif key == ZOOM and balance - bet >= 20:
            bet += 20

        elif key == TRCE and balance - bet >= 100:
            bet += 100

        elif key == GRPH and bet > 0:
            new_balance, quit_flag = play_round(balance - bet, bet)
            if quit_flag:
                break
            balance = new_balance
            bet     = 0

            if balance <= 0:
                draw_bg()
                set_menu(["", "", "", "QUIT", "PLAY"])

                end_text = "GAME OVER"
                x = max(0, (SCREEN_WIDTH - len(end_text) * CHAR_W) // 2)
                lbl(x, STATUS_Y, end_text)

                while True:
                    key = get_key(1)
                    if key == GRPH or key == TRCE or key == CLEAR_KEY:
                        break
                if key == TRCE or key == CLEAR_KEY:
                    break
                balance = STARTING_BALANCE
                bet     = 0

            draw_bet_screen(balance, bet)
            prev_bet_text = "Bet: $0"
            continue

        set_menu_btn(0, "CLEAR" if bet > 0 else "MAX")

        new_bet_text = "Bet: $" + str(bet)
        if new_bet_text != prev_bet_text:
            erase_lbl(4, 36, prev_bet_text)
            lbl(4, 36, new_bet_text)
            prev_bet_text = new_bet_text


run_game()
