import dis

src = """
from stdlib import *

def __setup__(self):
    self.health = 10

def __tick__(self, dt):
    speed = 0.01
    if keypressed == "w":
        self.move(speed + 0.01, 0, 0, dt)
    if keypressed == "s":
        self.move(-speed, 0, 0, dt)

    if keypressed == "a":
        self.move(0, 0, -speed, dt)
    if keypressed == "d":
        self.move(0, 0, speed, dt)

    thing = [0, 0]
    print(thing[1])
"""

dis.dis(src)