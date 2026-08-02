import random
import math
import turtle as t


class DotArtMaker:
    def __init__(self, screen, canvas_width, canvas_height, rgb_colors, dot_count):
        self.screen = screen
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.rgb_colors = rgb_colors
        # dot_count may be int or string; ensure int
        self.dot_count = int(dot_count)
        # optional explicit grid size (cols, rows) can be set by the caller
        self.grid_cols = None
        self.grid_rows = None
        self.artist = t.RawTurtle(screen)
        self.artist.hideturtle()
        self.artist.speed("fastest")
        self.artist.penup()

    def _grid(self):
        if self.grid_cols and self.grid_rows:
            return int(self.grid_cols), int(self.grid_rows)
        size = max(1, math.ceil(math.sqrt(self.dot_count)))
        return size, size

    def total_dots(self):
        cols, rows = self._grid()
        return min(self.dot_count, cols * rows)

    def draw_steps(self, recorder=None):
        """Generator that draws a single dot per iteration.

        Callers pace the animation by advancing the generator (e.g. via
        tkinter's `after`) instead of blocking with `time.sleep`, which
        used to freeze the whole application while drawing. If a
        RasterRecorder is supplied, every dot is mirrored into it so it can
        be exported to PNG/PDF without needing a screenshot of the canvas.
        """
        grid_cols, grid_rows = self._grid()

        margin = 80
        spacing_x = (self.canvas_width - margin) / max(grid_cols - 1, 1) if grid_cols > 1 else 50
        spacing_y = (self.canvas_height - margin) / max(grid_rows - 1, 1) if grid_rows > 1 else 50
        spacing = min(spacing_x, spacing_y)

        dot_size = max(6, min(24, int(spacing * 0.35)))
        start_x = -((grid_cols - 1) * spacing) / 2
        start_y = -((grid_rows - 1) * spacing) / 2

        self.screen.colormode(255)
        self.screen.tracer(0, 0)

        drawn = 0
        for row in range(grid_rows):
            for col in range(grid_cols):
                if drawn >= self.dot_count:
                    self.screen.update()
                    return
                color = random.choice(self.rgb_colors)
                x = start_x + col * spacing
                y = start_y + row * spacing
                self.artist.goto(x, y)
                self.artist.dot(dot_size, color)
                if recorder is not None:
                    recorder.dot(x, y, dot_size, color)
                drawn += 1
                self.screen.update()
                yield

        self.screen.update()
