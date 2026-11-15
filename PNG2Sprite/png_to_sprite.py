
from PIL import Image
import sys

MAX_WIDTH = 47
MAX_HEIGHT = 62
COLORS = 16


def convert_png(filename):

    img = Image.open(filename).convert("RGBA")
    img.thumbnail((MAX_WIDTH, MAX_HEIGHT))

    pixels = img.load()

    # Create RGB image for color reduction.
    rgb_img = Image.new("RGB", img.size, (0, 0, 0))

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]

            if a > 127:
                rgb_img.putpixel((x, y), (r, g, b))

    # Reduce to a maximum of 16 colors.
    quantized = rgb_img.quantize(colors=COLORS)
    indexes = quantized.load()

    width, height = img.size

    # Find only palette indexes actually used by visible pixels.
    used_colors = sorted({
        indexes[x, y]
        for y in range(height)
        for x in range(width)
        if pixels[x, y][3] > 127
    })

    palette_data = quantized.getpalette()

    # Build compact palette and remap original indexes.
    palette = []
    color_map = {}

    for new_index, old_index in enumerate(used_colors):
        i = old_index * 3

        r = palette_data[i]
        g = palette_data[i + 1]
        b = palette_data[i + 2]

        palette.append((r << 16) | (g << 8) | b)
        color_map[old_index] = new_index

    sprites = {}

    # Create a separate sprite for each used color.
    for old_color in used_colors:

        color = color_map[old_color]
        rectangles = []
        active = {}

        for y in range(height):

            runs = []
            x = 0

            while x < width:

                if pixels[x, y][3] <= 127:
                    x += 1
                    continue

                if indexes[x, y] != old_color:
                    x += 1
                    continue

                start = x

                while (
                    x < width
                    and pixels[x, y][3] > 127
                    and indexes[x, y] == old_color
                ):
                    x += 1

                runs.append((start, x - start))

            current = set(runs)

            # Finish rectangles that no longer continue.
            for key in list(active):

                if key not in current:
                    start_y = active.pop(key)
                    start_x, run_width = key
                    rect_height = y - start_y

                    rectangles.append(
                        (start_x, start_y, run_width, rect_height)
                    )

            # Start new rectangles.
            for key in current:

                if key not in active:
                    active[key] = y

        # Finish remaining rectangles.
        for key, start_y in active.items():

            start_x, run_width = key
            rect_height = height - start_y

            rectangles.append(
                (start_x, start_y, run_width, rect_height)
            )

        if not rectangles:
            continue

        encoded = [color]

        for x, y, w, h in rectangles:

            value = (
                ((x + 1) << 25)
                | ((y + 1) << 17)
                | (w << 8)
                | h
            )

            encoded.append(value)

        sprites[color] = encoded

    return width, height, palette, sprites


if __name__ == "__main__":

    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "input")
    output_dir = os.path.join(script_dir, "output")

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    png_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".png")]

    if not png_files:
        print(f"No PNG files found in {input_dir}")
    else:
        for png_file in png_files:
            input_path = os.path.join(input_dir, png_file)
            base_name = os.path.splitext(png_file)[0]
            output_path = os.path.join(output_dir, f"{base_name}_sprite_data.py")

            width, height, palette, sprites = convert_png(input_path)

            with open(output_path, "w") as f:
                f.write(f"{base_name}_palette = " + repr(palette) + "\n\n")
                f.write(f"{base_name}_sprites = " + repr(sprites) + "\n")

            print(f"Converted: {png_file}")
            print(f"  Dimensions: {width} x {height}")
            print(f"  Colors: {len(palette)}")
            print(f"  Palette: {[hex(c) for c in palette]}")
            print(f"  Saved to: {output_path}")
