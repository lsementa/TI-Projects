import ti_draw
import random
import ti_graphics
import ti_image
from ti_system import *
try:
    from micropython import const   # compiled (.8mp2): values built in
except ImportError:
    def const(x):                   # plain .py without micropython
        return x

# Dimensions
SCREEN_WIDTH  = const(321)
SCREEN_HEIGHT = const(211)
BUTTON_HEIGHT = const(22)
CHAR_W = const(10)

# Colors
BG_COLOR   = (53, 101, 77)
MENU_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
GOLD_COLOR = (255, 215, 0)
RED_SUITE  = (255, 0, 0)
BLACK_SUITE = (0, 0, 0)

# Keys
CLEAR_KEY = const(45)
YEQ  = const(11)   # F1 - MAX / CLEAR bet
WIN  = const(12)   # F2 - $5
ZOOM = const(13)   # F3 - $20
TRCE = const(14)   # F4 - $100 / HIT
GRPH = const(15)   # F5 - DEAL / STAY

RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
SUITS = ["S","H","D","C"]

STARTING_BALANCE = const(500)

_menu = ["", "", "", "", ""]

# card.png: 47 x 62
card_palette = [16777215, 16645629, 0]
card_sprites = {0: b'\x02\x01+\x01-\x02\x01\x01\x01\x02+\x01\x01\x03-9\x02<+\x01', 1: b',\x02\x01\x01', 2: b'\x02\x00+\x01\x01\x01\x01\x01-\x01\x01\x01\x00\x02\x01:.\x02\x01:\x01<\x01\x01-<\x01\x01\x02=+\x01'}

# back.png: 47 x 62
back_palette = [3107777, 16777215, 0]
back_sprites = {0: b'\x03\x03,9', 1: b'\x02\x01,\x02\x01\x02.\x01\x01\x03\x02:,\x03\x039\x03;,\x01\x03<+\x01', 2: b'\x02\x00+\x01\x01\x01\x01\x01-\x01\x01\x01\x00\x02\x01:.\x02\x01:\x01<\x01\x01-<\x01\x01\x02=+\x01'}

# TI_Logo.png: 26 x 26
TI_Logo_palette = [0]
TI_Logo_sprites = {0: b'\x07\x00\x06\t\x11\x01\x01\x03\x10\x02\x03\x02\r\x05\x02\x02\x10\x05\x02\x05\x13\x05\x05\x03\x18\x06\x01\x01\r\x07\x01\x01\x0f\x08\x03\x02\x14\x08\x05\t\x07\t\x05\x08\x00\n\x0c\x02\x0f\n\x02\x05\x0c\x0b\x01\x06\x12\x0b\x08\x05\x01\x0c\x0c\x01\x02\r\x0b\x01\x0e\r\x03\x02\x03\x0e\n\x02\x0e\x0f\x02\x01\x04\x10\t\x01\x13\x10\x06\x01\x04\x11\x03\x01\n\x11\x02\x01\x13\x11\x04\x01\x0b\x12\x02\x02\x13\x12\x02\x01\r\x13\x07\x01\x0c\x14\x07\x02\r\x16\x05\x02\x0e\x18\x05\x01\x0f\x19\x04\x01'}

# club.png: 25 x 25
club_palette = [2301728]
club_sprites = {0: b'\x0b\x00\x04\x13\t\x01\x07\x12\x08\x02\t\x11\x07\x03\x0b\x06\x12\x05\x01\x03\x11\t\x01\r\x05\n\x10\t\x03\x0b\x14\x08\x02\x0c\x16\x07\x01\r\x17\x06\x18\x0f\x01\x02\x02\x13\t\x01\x0c\x13\x0b\x01\x03\x14\x07\x01\x0c\x14\x02\x05\x0f\x14\x07\x01\x05\x15\x03\x01\x0b\x15\x03\x04\x12\x15\x02\x01\x0e\x16\x01\x03\n\x17\x05\x02\t\x18\x07\x01'}

# diamond.png: 22 x 25
diamond_palette = [16646144]
diamond_sprites = {0: b'\x0c\x01\x01\x18\x0b\x02\x03\x15\n\x03\x05\x13\t\x05\x07\x0f\x08\x06\t\r\x07\x07\x0b\x0b\x06\t\r\x07\x05\n\x0f\x05\x04\x0b\x11\x03\x03\x0c\x13\x01'}

# heart.png: 24 x 24
heart_palette = [16646144]
heart_sprites = {0: b'\x04\x02\x06\r\x0f\x02\x07\r\x03\x03\x08\x0b\x0e\x03\t\n\x02\x04\n\t\r\x04\n\t\x01\x05\x17\x06\x0c\x0b\x0c\x01\x0c\x0c\x0b\x01\x0b\r\x0b\x02\n\x0e\x0c\x01\x05\x0f\x10\x01\x06\x10\x0e\x01\x07\x11\x0c\x01\x08\x12\n\x01\t\x13\x08\x01\n\x14\x06\x01\x0b\x15\x03\x02\x0c\x17\x01\x01'}

# spade.png: 24 x 25
spade_palette = [2301728]
spade_sprites = {0: b'\x0c\x01\x02\x18\x0b\x02\x03\x11\n\x03\x05\x10\t\x04\x07\x0f\x08\x05\t\x0e\x07\x06\x0b\r\x06\x07\r\x0c\x05\x08\x0f\x0b\x04\t\x11\n\x03\n\x13\t\x02\x0b\x15\x08\x17\r\x01\x05\x01\x0e\x17\x03\x03\x13\x08\x01\x0e\x13\x08\x01\x04\x14\x06\x01\x0b\x14\x03\x05\x0f\x14\x06\x01\x0e\x16\x01\x03\n\x17\x05\x02\t\x18\x07\x01'}

# Card layout
CARD_W       = const(47)
CARD_H       = const(62)
CARD_SPACING = const(CARD_W - 23)   # overlap
DEALER_Y     = const(20)
PLAYER_Y     = const(109)

# Text y-positions for play screen
BAL_Y    = const(19)
D_VAL_Y  = const(85)
P_VAL_Y  = const(174)
STATUS_Y = const(104)   # center of gap between dealer and player

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


def clear_bg(x, y, w, h):
    if w > 2 and h > 2:
        ti_image.clear_image(x + 1, y + 1, w - 2, h - 2, BG_COLOR)
    elif w > 1 and h > 1:
        ti_draw.set_color(*BG_COLOR)
        ti_draw.fill_rect(x, y, w, h)


def draw_bg():
    clear_bg(-1, -1, SCREEN_WIDTH, SCREEN_HEIGHT - BUTTON_HEIGHT)


def draw_value(x, y, card_value, color=BLACK_SUITE):
    ti_draw.set_color(*color)
    ti_graphics.setFont(0)
    # top-left corner
    ti_draw.draw_text(x + 3, y + 20, card_value)
    # bottom-right corner
    text_width = len(card_value) * 9
    ti_draw.draw_text(x + 44 - text_width, y + 62, card_value)
    ti_graphics.setFont(1)


def draw_sprite(x, y, palette, sprites):
    for c in sprites:
        rgb = palette[c]
        ti_draw.set_color(rgb >> 16, (rgb >> 8) & 255, rgb & 255)
        r = sprites[c]
        for i in range(0, len(r), 4):
            ti_draw.fill_rect(x + r[i] - 1, y + r[i + 1] - 1,
                              r[i + 2] + 1, r[i + 3] + 1)


def sprite_center(sprites):
    # Center point of the sprite's bounding box (in sprite-local coords)
    min_x = min_y = 255
    max_x = max_y = 0
    for c in sprites:
        r = sprites[c]
        for i in range(0, len(r), 4):
            px = r[i]
            py = r[i + 1]
            if px < min_x: min_x = px
            if py < min_y: min_y = py
            if px + r[i + 2] > max_x: max_x = px + r[i + 2]
            if py + r[i + 3] > max_y: max_y = py + r[i + 3]
    return ((min_x + max_x) // 2, (min_y + max_y) // 2)


_card_cx, _card_cy = sprite_center(card_sprites)


def centered(palette, sprites):
    # (palette, sprites, dx, dy): dx/dy is the offset to add to the card's
    # (x, y) so the sprite lands centered on the card
    sx, sy = sprite_center(sprites)
    return (palette, sprites, _card_cx - sx, _card_cy - sy)


_logo  = centered(TI_Logo_palette, TI_Logo_sprites)
# Indexed by suit: 0 = spades, 1 = hearts, 2 = diamonds, 3 = clubs
_suits = (centered(spade_palette, spade_sprites),
          centered(heart_palette, heart_sprites),
          centered(diamond_palette, diamond_sprites),
          centered(club_palette, club_sprites))


def draw_sprite_centered(x, y, s):
    draw_sprite(x + s[2], y + s[3], s[0], s[1])


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


def draw_card(x, y, card_index):
    draw_sprite(x, y, card_palette, card_sprites)
    suit  = card_index // 13
    rank  = card_index % 13
    color = RED_SUITE if suit in (1, 2) else BLACK_SUITE
    draw_sprite_centered(x, y, _suits[suit])
    draw_value(x, y, RANKS[rank], color)


def draw_card_back_at(x, y):
    draw_sprite(x, y, back_palette, back_sprites)
    draw_sprite_centered(x, y, _logo)


def draw_hand(user, hand, count, hide_last=False):
    card_y = DEALER_Y if user == 1 else PLAYER_Y
    cards = _dealer_cards if user == 1 else _player_cards
    if count > 0:
        x0 = cards[0][0] - 2
        x1 = cards[count - 1][0] + CARD_W
        clear_bg(x0, card_y - 2, x1 - x0, CARD_H + 2)
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

    set_menu(["QUIT", "", "", "", "PLAY"])

    while True:
        key = get_key(1)
        if key == GRPH:
            return balance, False
        if key == YEQ or key == CLEAR_KEY:
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
                set_menu(["QUIT", "", "", "", "PLAY"])

                end_text = "GAME OVER"
                x = max(0, (SCREEN_WIDTH - len(end_text) * CHAR_W) // 2)
                lbl(x, STATUS_Y, end_text)

                while True:
                    key = get_key(1)
                    if key == GRPH or key == YEQ or key == CLEAR_KEY:
                        break
                if key == YEQ or key == CLEAR_KEY:
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
