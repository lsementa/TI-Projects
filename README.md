# TI-84 Evo Projects

A collection of games and tools for the **TI-84 Evo** calculator.

## Projects

### Snake

> `Snake/SNAKE.py`

Classic Snake game. Navigate the snake to eat apples without hitting the walls or yourself.

![Snake screenshot](Screenshots/snake.png)

---

### Blackjack

> `Blackjack/BLCKJACK.py`

A fully-featured Blackjack game. Cards are rendered with hand-drawn suits (spades, hearts, diamonds, clubs) using `ti_draw` polygons and a compact sprite system.

![Blackjack screenshot](Screenshots/blackjack1.png)  ![Backjack screenshot2](Screenshots/blackjack2.png)

**Features**
- Betting screen with balance tracking (starts at $500)
- Dealer hides second card until player stays
- Dealer draws to soft 17
- 5-Card Trick: collect 5 cards without busting to auto-win

---

### PNG2Sprite

> `PNG2Sprite/png_to_sprite.py`

A desktop Python utility that converts PNG images into sprite data compatible with the TI-84 `ti_draw` API.

**Requirements:** `Pillow`

```bash
pip install pillow
```

**Usage**

1. Place PNG files in `PNG2Sprite/input/`
2. Run the script: `python png_to_sprite.py`
3. Output `.py` files appear in `PNG2Sprite/output/`

Each output file contains a `palette` list (up to 16 colors as 24-bit integers) and a `sprs` dictionary of rectangle-encoded sprite data, ready to paste into a TI-84 Python script.

---
