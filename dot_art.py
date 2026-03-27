import random
import turtle as t


class DotArtMaker:
    def __init__(self, screen, canvas_width, canvas_height, rgb_colors, dot_count):
        self.screen = screen
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.rgb_colors = rgb_colors
        self.dot_count = int(dot_count)
        self.artist = t.RawTurtle(screen)
        self.artist.hideturtle()
        self.artist.speed("fastest")
        self.artist.penup()

    def create_dot_art(self):
        grid_size = int(self.dot_count ** 0.5)
        spacing = min(
            (self.canvas_width - 120) / max(grid_size - 1, 1),
            (self.canvas_height - 120) / max(grid_size - 1, 1),
        )
        dot_size = max(12, min(30, int(spacing * 0.45)))
        start_x = -((grid_size - 1) * spacing) / 2
        start_y = -((grid_size - 1) * spacing) / 2

        self.screen.colormode(255)
        self.screen.tracer(0, 0)

        for row in range(grid_size):
            for col in range(grid_size):
                color = random.choice(self.rgb_colors)
                self.artist.goto(start_x + col * spacing, start_y + row * spacing)
                self.artist.dot(dot_size, color)

        self.screen.update()
