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
            artist.penup()
            artist.pensize(random.randint(3, 9))
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

    def random_walk(self, num_steps, rgb_colors):
        self.screen.colormode(255)
        self.screen.tracer(0, 0)

        for artist in self.turtles:
            artist.pencolor(random.choice(rgb_colors))
            artist.pendown()

        for _ in range(num_steps):
            for artist in self.turtles:
                artist.setheading(random.choice(DIRECTIONS))
                artist.pencolor(random.choice(rgb_colors))
                artist.forward(self.walk_distance)

                if (
                    abs(artist.xcor()) > (self.canvas_width / 2 - self.margin)
                    or abs(artist.ycor()) > (self.canvas_height / 2 - self.margin)
                ):
                    self.keep_inside_canvas(artist)

            self.screen.update()

        self.screen.update()
