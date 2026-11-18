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
card_sprites = {0: [0, 100936449, 1543897345, 67513089, 67644729, 108669697], 1: [1, 1510342913], 2: [2, 100805377, 67371265, 1543766273, 33947962, 1577451834, 75104513, 1551499521, 108800769]}

# back.png: 47 x 62
back_palette = [929184, 16777215, 0]
back_sprites = {0: [0, 134753337], 1: [1, 100936706, 67513857, 67633722, 1510474553, 142093313, 142224129], 2: [2, 100805377, 67371265, 1543766273, 33947962, 1577451834, 75104513, 1551499521, 108800769]}

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
    ti_draw.draw_text(x + 44 - text_width, y + 62, card_value)
    ti_graphics.setFont(1)


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


_card      = prepare_sprite(card_palette, card_sprites)
_back      = prepare_sprite(back_palette, back_sprites)
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


def sprite_center(prepared):
    # Center point of the sprite's bounding box (in sprite-local coords)
    min_x = min_y = 9999
    max_x = max_y = -9999
    for sprite_id in prepared:
        for px, py, w, h in prepared[sprite_id][1]:
            if px < min_x: min_x = px
            if py < min_y: min_y = py
            if px + w > max_x: max_x = px + w
            if py + h > max_y: max_y = py + h
    return ((min_x + max_x) // 2, (min_y + max_y) // 2)


_card_cx, _card_cy = sprite_center(_card)
# Offset to add to the card's (x, y) so each suit sprite lands centered on the card
_suit_offsets = {}
for _s in (_heart, _diamond, _club, _spade):
    _sx, _sy = sprite_center(_s)
    _suit_offsets[id(_s)] = (_card_cx - _sx, _card_cy - _sy)


def draw_sprite_centered(x, y, prepared):
    dx, dy = _suit_offsets[id(prepared)]
    draw_sprite(x + dx, y + dy, prepared)


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
        draw_sprite_centered(x, y, _heart)
    elif suit == 2:
        draw_sprite_centered(x, y, _diamond)
    elif suit == 3:
        draw_sprite_centered(x, y, _club)
    else:
        draw_sprite_centered(x, y, _spade)


def draw_card(x, y, card_index):
    draw_sprite(x, y, _card)
    suit  = card_index // 13
    rank  = card_index % 13
    color = RED_SUITE if suit in (1, 2) else BLACK_SUITE
    _draw_suit(x, y, suit)
    draw_value(x, y, RANKS[rank], color)


def draw_card_back_at(x, y):
    draw_sprite(x, y, _back)


def draw_hand(user, hand, count, hide_last=False):
    card_y = DEALER_Y if user == 1 else PLAYER_Y
    cards = _dealer_cards if user == 1 else _player_cards
    if count > 0:
        x0 = cards[0][0] - 2
        x1 = cards[count - 1][0] + CARD_W
        ti_draw.set_color(*BG_COLOR)
        ti_draw.fill_rect(x0, card_y - 2, x1 - x0, CARD_H + 2)
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
