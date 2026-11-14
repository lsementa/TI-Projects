import ti_draw
import random
import time
from ti_system import *

# Screen Setup
SCREEN_WIDTH = 321
SCREEN_HEIGHT = 211
SQUARE_LENGTH = 10
SCORE_H = 22
BORDER = 2
BOARD_COLS = (SCREEN_WIDTH - 2 * BORDER) // SQUARE_LENGTH
BOARD_ROWS = (SCREEN_HEIGHT - SCORE_H - 2 * BORDER) // SQUARE_LENGTH
BOARD_X = (SCREEN_WIDTH - BOARD_COLS * SQUARE_LENGTH - 2 * BORDER) // 2
BOARD_Y = SCORE_H

# Colors
BG_COLOR = (0, 0, 0)            # Black
SNAKE_COLOR = (0, 255, 0)       # Green
APPLE_COLOR = (255, 0, 0)       # Red
TEXT_COLOR = (255, 255, 255)    # White        
BORDER_COLOR = (0, 0, 255)      # Blue

# Keyboard Codes
UP = 25
DOWN = 34
LEFT = 24
RIGHT = 26
CLEAR = 45
ENTER = 105

# Direction vectors
DIRECTIONS = {
    UP:    (0, -1),
    DOWN:  (0,  1),
    LEFT:  (-1, 0),
    RIGHT: (1,  0),
}

# Prevent 180-degree reversal
OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# Width of one character in ti_draw's default font
CHAR_W = 10

SPEED = 0.15  # seconds per step

def draw_bg():
    r, g, b = BG_COLOR
    ti_draw.set_color(r, g, b)
    ti_draw.fill_rect(-1, -1, SCREEN_WIDTH, SCREEN_HEIGHT)

def draw_cell(col, row, color):
    r, g, b = color
    ti_draw.set_color(r, g, b)
    ti_draw.fill_rect(BOARD_X + BORDER + col * SQUARE_LENGTH,
                      BOARD_Y + BORDER + row * SQUARE_LENGTH,
                      SQUARE_LENGTH, SQUARE_LENGTH)

def draw_score(score):
    r, g, b = BG_COLOR
    ti_draw.set_color(r, g, b)
    ti_draw.fill_rect(0, 0, SCREEN_WIDTH, SCORE_H)
    r, g, b = TEXT_COLOR
    ti_draw.set_color(r, g, b)
    score_text = "Score: " + str(score)
    x = SCREEN_WIDTH - len(score_text) * CHAR_W - 5 # Padding 5 pixels
    ti_draw.draw_text(x, SCORE_H, score_text)

def draw_border():
    r, g, b = BORDER_COLOR
    ti_draw.set_color(r, g, b)
    ti_draw.fill_rect(BOARD_X, BOARD_Y,
                      BOARD_COLS * SQUARE_LENGTH + 2 * BORDER,
                      BOARD_ROWS * SQUARE_LENGTH + 2 * BORDER)
    r, g, b = BG_COLOR
    ti_draw.set_color(r, g, b)
    ti_draw.fill_rect(BOARD_X + BORDER, BOARD_Y + BORDER,
                      BOARD_COLS * SQUARE_LENGTH,
                      BOARD_ROWS * SQUARE_LENGTH)

def place_apple(snake):
    while True:
        col = random.randint(0, BOARD_COLS - 1)
        row = random.randint(0, BOARD_ROWS - 1)
        if (col, row) not in snake:
            return (col, row)

def show_game_over(score):
    draw_bg()
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2
    game_over_text = "GAME OVER"
    end_text = "[ENTER] / [CLEAR]"
    score_text = "Score: " + str(score)
    r, g, b = APPLE_COLOR
    ti_draw.set_color(r, g, b)
    ti_draw.draw_text(cx - len(game_over_text) * CHAR_W // 2, cy - 25, game_over_text)
    r, g, b = BORDER_COLOR
    ti_draw.set_color(r, g, b)
    ti_draw.draw_text(cx - len(score_text)     * CHAR_W // 2, cy,      score_text)
    r, g, b = TEXT_COLOR
    ti_draw.set_color(r, g, b)
    ti_draw.draw_text(cx - len(end_text)       * CHAR_W // 2, cy + 35, end_text)

def run_game():
    draw_bg()
    draw_score(0)
    draw_border()

    start_col = BOARD_COLS // 2
    start_row = BOARD_ROWS // 2
    snake = [(start_col, start_row)]
    direction = RIGHT
    score = 0

    apple = place_apple(snake)
    draw_cell(apple[0], apple[1], APPLE_COLOR)
    draw_cell(snake[0][0], snake[0][1], SNAKE_COLOR)

    last_move = time.monotonic()

    while True:
        key = get_key(0)

        if key == CLEAR:
            return False  # quit

        if key in DIRECTIONS and key != OPPOSITES[direction]:
            direction = key

        if time.monotonic() - last_move < SPEED:
            continue

        last_move = time.monotonic()

        dcol, drow = DIRECTIONS[direction]
        head_col, head_row = snake[0]
        new_col = head_col + dcol
        new_row = head_row + drow

        # Wall collision
        if not (0 <= new_col < BOARD_COLS and 0 <= new_row < BOARD_ROWS):
            show_game_over(score)
            return None  # wait for restart choice

        new_head = (new_col, new_row)

        # Self collision
        if new_head in snake:
            show_game_over(score)
            return None

        snake.insert(0, new_head)
        draw_cell(new_col, new_row, SNAKE_COLOR)

        if new_head == apple:
            score += 1
            draw_score(score)
            apple = place_apple(snake)
            draw_cell(apple[0], apple[1], APPLE_COLOR)
        else:
            tail = snake.pop()
            draw_cell(tail[0], tail[1], BG_COLOR)

# Main loop
while True:
    result = run_game()
    if result is False:
        break
    # Game over: wait for ENTER to restart or CLEAR to quit
    while True:
        key = get_key(0)
        if key == ENTER:
            break
        if key == CLEAR:
            result = False
            break
    if result is False:
        break
