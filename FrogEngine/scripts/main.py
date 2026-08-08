from scripts.stdlib import *

def __setup__(self):
    self.health = 10

def __tick__(self, dt):
    speed = 0.01
    x_speed = speed[0]
    z_speed = speed[1]
    if self == "Self|Model|bob":
        self.rotate(0, 0.1, 0)
    if keypressed == "w":
        self.move(-x_speed, 0, 0)
    if keypressed == "s":
        self.move(x_speed, 0, 0)

    if keypressed == "a":
        self.move(0, 0, z_speed)
    if keypressed == "d":
        self.move(0, 0, -z_speed)