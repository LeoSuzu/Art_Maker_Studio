import math
import random
import turtle as t


class CircleArt:
    def __init__(self, screen, canvas_width, canvas_height):
        self.screen = screen
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.artist = t.RawTurtle(screen)
        self.artist.speed("fastest")
        self.artist.hideturtle()
        self.artist.penup()

    def position(self, radius):
        margin = radius + 10
        half_width = max(1, int(self.canvas_width / 2 - margin))
        half_height = max(1, int(self.canvas_height / 2 - margin))
        position_x = random.randint(-half_width, half_width)
        position_y = random.randint(-half_height, half_height)
        return position_x, position_y

    def total_strokes(self, circle_count):
        return int(circle_count)

    def draw_steps(self, rgb_colors, circle_count, thickness, radius, recorder=None):
        """Generator that draws exactly `circle_count` circles, one per
        iteration, all sharing the same `thickness` and `radius` — only the
        color is randomized per circle. Previously size and thickness were
        also randomized per circle, which made the "5 circles" / "14
        circles" selector feel arbitrary rather than a real size control.
        """
        max_possible_radius = max(10, min(self.canvas_width, self.canvas_height) // 2 - 20)
        radius = max(10, min(int(radius), max_possible_radius))
        thickness = max(1, int(thickness))

        self.screen.colormode(255)
        self.screen.tracer(0, 0)

        for _ in range(int(circle_count)):
            x, y = self.position(radius)
            heading = random.randint(0, 360)
            color = random.choice(rgb_colors)

            self.artist.goto(x, y)
            self.artist.setheading(heading)
            self.artist.pensize(thickness)
            self.artist.pencolor(color)
            self.artist.pendown()
            self.artist.circle(radius)
            self.artist.penup()

            if recorder is not None:
                left_angle_rad = math.radians(heading + 90)
                center_x = x + radius * math.cos(left_angle_rad)
                center_y = y + radius * math.sin(left_angle_rad)
                recorder.circle_outline(center_x, center_y, radius, thickness, color)

            self.screen.update()
            yield

        self.screen.update()
