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

    def position(self):
        position_x = random.randint(int(-self.canvas_width / 2) + 90, int(self.canvas_width / 2) - 90)
        position_y = random.randint(int(-self.canvas_height / 2) + 90, int(self.canvas_height / 2) - 90)
        return position_x, position_y

    def draw_art(self, rgb_colors, circle_count):
        max_radius = max(40, min(self.canvas_width, self.canvas_height) // 3)
        self.screen.colormode(255)
        self.screen.tracer(0, 0)

        for _ in range(int(circle_count)):
            self.artist.penup()
            self.artist.goto(self.position())
            self.artist.setheading(random.randint(0, 360))
            self.artist.pensize(random.randint(8, 24))

            for _ in range(18):
                self.artist.pencolor(random.choice(rgb_colors))
                self.artist.pendown()
                self.artist.circle(random.randint(max_radius // 3, max_radius))
                self.artist.left(20)
                self.artist.penup()

        self.screen.update()
