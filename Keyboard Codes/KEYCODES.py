import ti_draw
import ti_system

BG_COLOR = (255, 255, 255) # White
TXT_COLOR = (0, 0, 0) # Black
old_result = ""

ti_draw.set_color(*TXT_COLOR)
ti_draw.draw_text(10, 20, "Press any key (CLEAR to quit):")

while True:
  k = ti_system.get_key(0)
  if k:
    if k == 45:  # 45 is the CLEAR key
      break
    result = "Key code: " + str(k)
    # Erase the old number
    ti_draw.set_color(*BG_COLOR)
    ti_draw.draw_text(10, 50, old_result)
    # Draw the new number
    ti_draw.set_color(*TXT_COLOR)
    ti_draw.draw_text(10, 50, result)
    old_result = result
