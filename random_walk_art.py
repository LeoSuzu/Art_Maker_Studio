import random
import turtle as t


DIRECTIONS = [0, 90, 180, 270]


class RandomWalkArt:
    def __init__(self, screen, canvas_width, canvas_height, turtle_count=48):
        self.screen = screen
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.turtle_count = turtle_count
        self.walk_distance = max(12, min(canvas_width, canvas_height) // 24)
        self.margin = 36
        self.turtles = self.create_multiple_turtles()

    def create_multiple_turtles(self):
        turtles = []
        for _ in range(self.turtle_count):
            artist = t.RawTurtle(self.screen)
            artist.hideturtle()
            # penup() before goto() means this jump to a random spawn point
            # never draws a line back to the canvas center.
            artist.penup()
            artist.pensize(4)  # Consistent pen size for all turtles
            artist.speed("fastest")
            artist.goto(self.random_position())
            artist.setheading(random.choice(DIRECTIONS))
            turtles.append(artist)
        return turtles

    def random_position(self):
        half_width = self.canvas_width / 2 - self.margin
        half_height = self.canvas_height / 2 - self.margin
        return (
            random.randint(int(-half_width), int(half_width)),
            random.randint(int(-half_height), int(half_height)),
        )

    def keep_inside_canvas(self, artist):
        half_width = self.canvas_width / 2 - self.margin
        half_height = self.canvas_height / 2 - self.margin

        x = max(min(artist.xcor(), half_width), -half_width)
        y = max(min(artist.ycor(), half_height), -half_height)
        artist.penup()
        artist.goto(x, y)
        artist.setheading(random.choice(DIRECTIONS))
        artist.pendown()

    def draw_steps(self, num_steps, rgb_colors, recorder=None):
        """Generator that advances every turtle by one step per iteration.

        Callers pace the animation (e.g. via tkinter's `after`) so the
        walk is visible instead of completing instantly. If a
        RasterRecorder is supplied, each forward step is mirrored into it
        so the result can be exported to PNG/PDF without screenshotting
        the canvas.
        """
        self.screen.colormode(255)
        self.screen.tracer(0, 0)

        for artist in self.turtles:
            artist.pencolor(random.choice(rgb_colors))
            artist.pendown()

        half_width = self.canvas_width / 2 - self.margin
        half_height = self.canvas_height / 2 - self.margin

        for _ in range(num_steps):
            for artist in self.turtles:
                if abs(artist.xcor()) > half_width or abs(artist.ycor()) > half_height:
                    self.keep_inside_canvas(artist)

                artist.setheading(random.choice(DIRECTIONS))
                color = random.choice(rgb_colors)
                artist.pencolor(color)

                if recorder is not None:
                    x0, y0 = artist.position()
                    artist.forward(self.walk_distance)
                    x1, y1 = artist.position()
                    recorder.line(x0, y0, x1, y1, 4, color)
                else:
                    artist.forward(self.walk_distance)

            self.screen.update()
            yield

        self.screen.update()
