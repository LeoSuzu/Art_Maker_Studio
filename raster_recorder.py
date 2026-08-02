from PIL import Image, ImageDraw


class RasterRecorder:
    """Mirrors turtle drawing commands onto an in-memory Pillow image.

    Exporting used to take a screenshot of the turtle window (via
    PIL.ImageGrab), which on macOS silently fails without the "Screen
    Recording" permission — the PNG export would error out while the
    PostScript export (which doesn't need a screenshot) kept working.
    Drawing the same shapes directly into a Pillow image as the art is
    generated sidesteps that permission entirely and is also faster.

    World coordinates match the turtle screen's: (0, 0) is the canvas
    center, x grows right, y grows up.
    """

    def __init__(self, width, height, bg="white"):
        self.width = int(width)
        self.height = int(height)
        self.image = Image.new("RGB", (self.width, self.height), bg)
        self.draw = ImageDraw.Draw(self.image)

    def _to_pixel(self, x, y):
        return (x + self.width / 2, self.height / 2 - y)

    def dot(self, x, y, diameter, color):
        px, py = self._to_pixel(x, y)
        r = diameter / 2
        self.draw.ellipse([px - r, py - r, px + r, py + r], fill=color)

    def line(self, x1, y1, x2, y2, width, color):
        p1 = self._to_pixel(x1, y1)
        p2 = self._to_pixel(x2, y2)
        width = max(1, int(round(width)))
        self.draw.line([p1, p2], fill=color, width=width)
        if width > 2:
            # round off the line caps so thick strokes don't look blocky
            r = width / 2
            for px, py in (p1, p2):
                self.draw.ellipse([px - r, py - r, px + r, py + r], fill=color)

    def circle_outline(self, center_x, center_y, radius, width, color):
        px, py = self._to_pixel(center_x, center_y)
        bbox = [px - radius, py - radius, px + radius, py + radius]
        self.draw.ellipse(bbox, outline=color, width=max(1, int(round(width))))

    def save_png(self, path):
        self.image.save(path)

    def save_pdf(self, path):
        self.image.convert("RGB").save(path, "PDF")
