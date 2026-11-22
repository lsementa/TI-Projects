
from PIL import Image
import sys

MAX_WIDTH = 4000
MAX_HEIGHT = 4000
COLORS = 2          # fewer colors = far fewer rectangles = faster drawing
REMOVE_HALO = True  # drop near-white anti-alias fringe touching the outside
HALO_LEVEL = 200    # a pixel is "near-white" if R, G and B are all >= this
SCALE = 16          # percent to resize every input image by (50 = half size)
                    # override from the command line: python png_to_sprite.py 50
SMOOTH_SCALE = False # False = nearest neighbor (crisp pixel art, fewer colors)
                      # True  = smooth/averaged (better for photos, more rects)

# Low-rect mode. Every fill_rect costs ~8 ms on the calculator no matter how
# big it is, so for moving game sprites it is worth trading a little detail
# for far fewer rectangles.
MAX_RECTS = 0         # 0 = exact cover. N > 0 = approximate the sprite's
                      # silhouette with at most N rectangles (other colors such
                      # as eyes stay exact and are drawn on top).
                      # command line: --max-rects 8
APPROX_PENALTY = 2.5  # how strongly approximation avoids painting outside the
                      # shape (higher = tighter fit, may miss thin parts)
FILL_HOLES = False    # fill transparent holes inside the shape (turns an
                      # outline into a solid silhouette). command line: --fill

# Output type
MAKE_8XV2 = False     # False = one sprites.py with every palette and sprite
                      # True  = a NAME.8xv2 calculator image per PNG, drawn with
                      #         ti_graphics.drawImage("NAME", x, y). File names
                      #         must be 8 characters max. command line: --8xv2


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


def fill_holes(grid, width, height):
    """Fill each row between its leftmost and rightmost pixel with the most
    common color. Turns outlines into solid silhouettes, even when the outline
    has small gaps (a flood fill would leak through those)."""
    counts = {}
    for c in grid.values():
        counts[c] = counts.get(c, 0) + 1
    fill = max(counts, key=counts.get)
    filled = dict(grid)
    for y in range(height):
        row = [x for x in range(width) if (x, y) in grid]
        if row:
            for x in range(min(row), max(row) + 1):
                if (x, y) not in filled:
                    filled[(x, y)] = fill
    return filled


def approximate_rects(mask, max_rects, penalty):
    """Greedy cover of `mask` (a set of (x, y)) with at most max_rects rects.

    Each step adds the rectangle that paints the most still-uncovered shape
    pixels minus `penalty` per background pixel it would paint. For each pair
    of rows the best column range is found with a max-subarray scan.
    """
    xs = [p[0] for p in mask]
    ys = [p[1] for p in mask]
    x_min, y_min = min(xs), min(ys)
    width = max(xs) - x_min + 1
    height = max(ys) - y_min + 1
    # value of painting each pixel: +1 uncovered shape, -penalty background
    value = [[(1.0 if (x + x_min, y + y_min) in mask else -penalty)
              for x in range(width)] for y in range(height)]
    rectangles = []
    while len(rectangles) < max_rects:
        best = (0.5, None)
        for y0 in range(height):
            col = [0.0] * width
            for y1 in range(y0, height):
                row = value[y1]
                for x in range(width):
                    col[x] += row[x]
                run, start = 0.0, 0
                for x in range(width):
                    if run <= 0:
                        run, start = 0.0, x
                    run += col[x]
                    if run > best[0]:
                        best = (run, (start, y0, x - start + 1, y1 - y0 + 1))
        if best[1] is None:
            break
        x, y, w, h = best[1]
        rectangles.append((x + x_min, y + y_min, w, h))
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                value[yy][xx] = 0.0      # already painted: no gain, no cost
    return rectangles


def encode_rect(x, y, w, h):
    return ((x + 1) << 25) | ((y + 1) << 17) | (w << 8) | h


def scale_image(img, percent):
    if percent == 100:
        return img
    w = max(1, round(img.width * percent / 100))
    h = max(1, round(img.height * percent / 100))
    resample = Image.LANCZOS if SMOOTH_SCALE else Image.NEAREST
    return img.resize((w, h), resample)


# --- Calculator image files (.8xv2, "IM8C") ------------------------------------
# One ti_graphics.drawImage("NAME", x, y) call draws a whole image natively,
# about as fast as a single fill_rect. Format matches TI-Planet's img2calc
# output byte for byte: a CBOR container around an RLE-compressed,
# palette-indexed image, plus the Evo XOR checksum.

def rgb565(c):
    r, g, b = (c >> 16) & 255, (c >> 8) & 255, c & 255
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def im8c_rle(pixels):
    """0x80|(n-2), color = run of n (2..128); n-1, colors... = n literals."""
    out = bytearray()
    lit = []

    def flush():
        while lit:
            chunk = lit[:128]
            del lit[:128]
            out.append(len(chunk) - 1)
            out.extend(chunk)

    i, n = 0, len(pixels)
    while i < n:
        j = i
        while j < n and pixels[j] == pixels[i] and j - i < 128:
            j += 1
        if j - i >= 2:
            flush()
            out.append(0x80 | (j - i - 2))
            out.append(pixels[i])
            i = j
        else:
            lit.append(pixels[i])
            i += 1
    flush()
    return bytes(out)


def _cbor_head(major, n):
    if n < 24:
        return bytes([(major << 5) | n])
    if n < 256:
        return bytes([(major << 5) | 24, n])
    return bytes([(major << 5) | 25, n >> 8, n & 255])


def _cbor_text(s):
    return _cbor_head(3, len(s)) + s.encode()


def _cbor_bytes(b):
    return _cbor_head(2, len(b)) + b


def _var_name(name):
    out = bytearray()
    for ch in name:
        if "A" <= ch <= "Z":
            w = 0xE800 + ord(ch) - 65
        elif "0" <= ch <= "9":
            w = 0xE401 + ord(ch) - 48
        else:
            raise ValueError(f"image name {name!r}: only A-Z and 0-9 allowed")
        out += bytes([w & 255, w >> 8])
    return bytes(out) + b"\0\0"


def evo_checksum(body):
    adjusted = len(body) - 3
    words = adjusted >> 1
    if adjusted & 1 and words > 0:
        words -= 1
    c = 0
    for i in range(words):
        c ^= body[2 * i] | (body[2 * i + 1] << 8)
    return c & 0xFFFF


def im8c_file(name, width, height, palette, pixels, transparent=False):
    """Bytes of a NAME.8xv2 image var.

    palette: 24-bit RGB ints (stored as RGB565); pixels: palette indexes,
    row by row. transparent=True makes palette index 0 transparent.
    """
    if len(name) > 8:
        raise ValueError(f"image name {name!r} is longer than 8 characters")
    assert len(pixels) == width * height
    img = b"IM8C" + b"".join(
        v.to_bytes(2, "little")
        for v in (2, width, height, 1 if transparent else 0, len(palette)))
    img += b"".join(rgb565(c).to_bytes(2, "little") for c in palette)
    img += im8c_rle(pixels)
    data = len(img).to_bytes(2, "little") + img
    body = (b"\xbf" + _cbor_text("metaData") + b"\xbf"
            + _cbor_text("type") + _cbor_head(0, 8)
            + _cbor_text("version") + _cbor_head(0, 1)
            + _cbor_text("flags") + _cbor_head(0, 1)
            + _cbor_text("name") + _cbor_bytes(_var_name(name)) + b"\xff"
            + _cbor_text("version") + _cbor_head(0, 1)
            + _cbor_text("size") + _cbor_head(0, len(data))
            + _cbor_text("data") + _cbor_bytes(data) + b"\xff")
    return body + evo_checksum(body).to_bytes(2, "big")


def grid_to_image(width, height, palette, grid):
    """Transparent background: index 0 = transparent, sprite colors after."""
    pixels = [0 if (x, y) not in grid else grid[(x, y)] + 1
              for y in range(height) for x in range(width)]
    return [0] + list(palette), pixels


def load_grid(filename, scale=SCALE):
    """PNG -> (width, height, palette, grid) with grid {(x, y): color index}.
    Colors are reduced and ordered most-pixels-first."""
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
        cleaned = remove_halo(visible, width, height)
        if cleaned:
            visible = cleaned
        else:
            # The whole image is light (e.g. a pale outline). Removing the
            # "halo" would erase everything, so keep it as is.
            print("  Halo removal skipped: image is entirely light colors")

    if not visible:
        sys.exit(f"{filename}: no visible pixels to convert")

    if FILL_HOLES:
        visible = fill_holes(visible, width, height)

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
    return width, height, palette, grid


def convert_png(filename, scale=SCALE):
    width, height, palette, grid = load_grid(filename, scale)
    sprites = encode_sprites(grid, len(palette))

    if MAX_RECTS > 0:
        # Color 0 is drawn first and later colors paint over it, so color 0
        # can cover the whole silhouette approximately.
        rects = approximate_rects(set(grid), MAX_RECTS, APPROX_PENALTY)
        sprites[0] = [0] + [encode_rect(*r) for r in rects]

    return width, height, palette, sprites


if __name__ == "__main__":

    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "input")
    output_dir = os.path.join(script_dir, "output")

    # Flags: --max-rects N, --fill, --8xv2. Everything else is [scale] [files...]
    IM8C = MAKE_8XV2
    COMBINED_NAME = "sprites.py"   # all palettes and sprites go in this one file
    args = []
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--max-rects":
            if i + 1 >= len(argv) or not argv[i + 1].isdigit():
                sys.exit("--max-rects needs a number, e.g. --max-rects 8")
            MAX_RECTS = int(argv[i + 1])
            i += 2
            continue
        if a == "--fill":
            FILL_HOLES = True
        elif a in ("--8xv2", "--im8c"):
            IM8C = True     # write NAME.8xv2 images for ti_graphics.drawImage
        else:
            args.append(a)
        i += 1
    sys.argv = sys.argv[:1] + args

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

    # Optional file names after the scale convert only those images:
    #   python png_to_sprite.py 100 cloud.png
    if len(sys.argv) > 2:
        wanted = {os.path.basename(a).lower() for a in sys.argv[2:]}
        png_files = [f for f in png_files if f.lower() in wanted]

    png_files.sort(key=str.lower)

    if not png_files:
        print(f"No PNG files found in {input_dir}")

    elif IM8C:
        # The file name becomes the calculator variable name, so check every
        # name before converting anything: at most 8 characters, letters and
        # digits only, starting with a letter.
        bad = []
        for png_file in png_files:
            base = os.path.splitext(png_file)[0]
            if len(base) > 8:
                bad.append(f"  {png_file}: {len(base)} characters (max 8)")
            elif not (base.isascii() and base.isalnum() and base[0].isalpha()):
                bad.append(f"  {png_file}: use only letters and digits, "
                           "starting with a letter")
        if bad:
            sys.exit("Rename these files before converting to .8xv2:\n" + "\n".join(bad))

        for png_file in png_files:
            name = os.path.splitext(png_file)[0].upper()
            w, h, pal, grid = load_grid(os.path.join(input_dir, png_file), scale)
            pal, pixels = grid_to_image(w, h, pal, grid)
            with open(os.path.join(output_dir, name + ".8xv2"), "wb") as f:
                f.write(im8c_file(name, w, h, pal, pixels, transparent=True))
            print(f"Converted: {png_file} -> {name}.8xv2  ({w} x {h})")
        print(f"Saved {len(png_files)} image(s) to {output_dir}")
        print('On the calculator: from ti_graphics import drawImage; '
              'drawImage("NAME", x, y)')

    else:
        # One Python file with every image's palette and sprites.
        lines = ["# Generated by png_to_sprite.py (scale %g%%)\n" % scale]
        for png_file in png_files:
            base = os.path.splitext(png_file)[0]
            ident = "".join(ch if ch.isalnum() else "_" for ch in base)
            if ident[0].isdigit():
                ident = "_" + ident
            width, height, palette, sprites = convert_png(
                os.path.join(input_dir, png_file), scale)
            lines.append(f"\n# {png_file}: {width} x {height}\n")
            lines.append(f"{ident}_palette = {palette!r}\n")
            lines.append(f"{ident}_sprites = {sprites!r}\n")
            print(f"Converted: {png_file}  ({width} x {height}, "
                  f"{len(palette)} colors, "
                  f"{sum(len(v) - 1 for v in sprites.values())} rectangles)")
        output_path = os.path.join(output_dir, COMBINED_NAME)
        with open(output_path, "w") as f:
            f.writelines(lines)
        print(f"Saved {len(png_files)} image(s) to {output_path}")
