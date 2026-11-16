
from PIL import Image
import sys

MAX_WIDTH = 400
MAX_HEIGHT = 400
COLORS = 3          # fewer colors = far fewer rectangles = faster drawing
REMOVE_HALO = True  # drop near-white anti-alias fringe touching the outside
HALO_LEVEL = 200    # a pixel is "near-white" if R, G and B are all >= this
SCALE = 50         # percent to resize every input image by (50 = half size)
                    # override from the command line: python png_to_sprite.py 50
SMOOTH_SCALE = False  # False = nearest neighbor (crisp pixel art, fewer colors)
                      # True  = smooth/averaged (better for photos, more rects)


def is_light(rgb):
    return min(rgb) >= HALO_LEVEL


def remove_halo(grid, width, height):
    """Make near-white pixels transparent when they connect to the outside.

    Interior whites (eyes, highlights) are kept because the flood fill
    can't reach them through darker pixels.
    """
    outside = set()
    stack = [(-1, -1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in outside or not (-1 <= x <= width and -1 <= y <= height):
            continue
        c = grid.get((x, y))
        if c is not None and not is_light(c):
            continue
        outside.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return {p: c for p, c in grid.items() if p not in outside}


def merge_colors(palette, grid, target):
    """Repeatedly merge the two most similar colors until `target` remain.

    PIL's quantizers tend to split near-identical shades on tiny sprites;
    this keeps visually distinct colors (like a white eye) instead.
    """
    rgbs = [[(c >> 16) & 255, (c >> 8) & 255, c & 255] for c in palette]
    counts = [0] * len(palette)
    for c in grid.values():
        counts[c] += 1
    alive = list(range(len(palette)))
    owner = list(range(len(palette)))

    while len(alive) > target:
        best = None
        for i in range(len(alive)):
            for j in range(i + 1, len(alive)):
                a, b = rgbs[alive[i]], rgbs[alive[j]]
                d = sum((a[k] - b[k]) ** 2 for k in range(3))
                if best is None or d < best[0]:
                    best = (d, alive[i], alive[j])
        _, a, b = best
        # Keep the color with more pixels so dominant shades stay exact.
        keep, drop = (a, b) if counts[a] >= counts[b] else (b, a)
        counts[keep] += counts[drop]
        alive.remove(drop)
        for k in range(len(owner)):
            if owner[k] == drop:
                owner[k] = keep

    new_index = {c: i for i, c in enumerate(alive)}
    new_palette = [palette[c] for c in alive]
    return new_palette, {p: new_index[owner[c]] for p, c in grid.items()}


def order_colors(palette, grid):
    """Renumber colors in draw order: most pixels first.

    Drawing big areas first lets later (smaller) colors paint over them,
    so earlier colors can use larger rectangles.
    """
    counts = {}
    for c in grid.values():
        counts[c] = counts.get(c, 0) + 1
    order = sorted(counts, key=lambda c: -counts[c])
    remap = {old: new for new, old in enumerate(order)}
    return ([palette[c] for c in order],
            {p: remap[c] for p, c in grid.items()})


def encode_sprites(grid, num_colors):
    """Greedy rectangle cover per color, allowing overdraw by later colors."""
    sprites = {}
    for color in range(num_colors):

        def ok(p):
            c = grid.get(p)
            return c is not None and c >= color

        covered = set()
        rectangles = []
        for p in sorted((p for p, c in grid.items() if c == color),
                        key=lambda p: (p[1], p[0])):
            if p in covered:
                continue
            x, y = p
            w = 1
            while ok((x + w, y)):
                w += 1
            h = 1
            while all(ok((x + i, y + h)) for i in range(w)):
                h += 1
            rectangles.append((x, y, w, h))
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    covered.add((xx, yy))

        if not rectangles:
            continue

        encoded = [color]
        for x, y, w, h in rectangles:
            encoded.append(((x + 1) << 25) | ((y + 1) << 17) | (w << 8) | h)
        sprites[color] = encoded
    return sprites


def scale_image(img, percent):
    if percent == 100:
        return img
    w = max(1, round(img.width * percent / 100))
    h = max(1, round(img.height * percent / 100))
    resample = Image.LANCZOS if SMOOTH_SCALE else Image.NEAREST
    return img.resize((w, h), resample)


def convert_png(filename, scale=SCALE):

    img = Image.open(filename).convert("RGBA")
    original_size = img.size
    img = scale_image(img, scale)
    img.thumbnail((MAX_WIDTH, MAX_HEIGHT))
    print(f"Resized {original_size[0]} x {original_size[1]} -> "
          f"{img.width} x {img.height} ({scale}%)")

    pixels = img.load()
    width, height = img.size

    # Visible pixels only: (x, y) -> (r, g, b)
    visible = {}
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a > 127:
                visible[(x, y)] = (r, g, b)

    if REMOVE_HALO:
        visible = remove_halo(visible, width, height)

    # Reduce colors using only visible pixels (transparent areas would
    # otherwise pull the palette toward the fill color).
    points = list(visible)
    strip = Image.new("RGB", (max(1, len(points)), 1))
    strip.putdata([visible[p] for p in points])
    quantized = strip.quantize(colors=16)
    indexes = quantized.load()
    palette_data = quantized.getpalette()

    palette = []
    color_map = {}
    grid = {}
    for i, p in enumerate(points):
        old = indexes[i, 0]
        if old not in color_map:
            color_map[old] = len(palette)
            r, g, b = palette_data[old * 3:old * 3 + 3]
            palette.append((r << 16) | (g << 8) | b)
        grid[p] = color_map[old]

    palette, grid = merge_colors(palette, grid, COLORS)

    palette, grid = order_colors(palette, grid)
    sprites = encode_sprites(grid, len(palette))

    return width, height, palette, sprites


if __name__ == "__main__":

    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "input")
    output_dir = os.path.join(script_dir, "output")

    scale = SCALE
    if len(sys.argv) > 1:
        try:
            scale = float(sys.argv[1].rstrip("%"))
        except ValueError:
            sys.exit(f"Scale must be a percent, e.g. 50 or 50% (got {sys.argv[1]!r})")
        if scale <= 0:
            sys.exit("Scale must be greater than 0")

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

            width, height, palette, sprites = convert_png(input_path, scale)

            with open(output_path, "w") as f:
                f.write(f"{base_name}_palette = " + repr(palette) + "\n\n")
                f.write(f"{base_name}_sprites = " + repr(sprites) + "\n")

            print(f"Converted: {png_file}")
            print(f"  Dimensions: {width} x {height}")
            print(f"  Colors: {len(palette)}")
            print(f"  Rectangles: {sum(len(v) - 1 for v in sprites.values())}")
            print(f"  Palette: {[hex(c) for c in palette]}")
            print(f"  Saved to: {output_path}")
