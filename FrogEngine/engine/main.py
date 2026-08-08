import engine as engine
import FLAMEACID

variables = {
            "dt": 1,
            "self": ["i am an self"],
        }

window = FLAMEACID.Window3D((800, 600), "smth")

camera = engine.Camera((5, 5, 5), (64, 0, 60), "help me")

camera.attach_script("scripts/main.py")
camera.run_script(variables, "__setup__")

window.set_camera(camera())

test_object = engine.FrogObject("Untitled.obj", (0, 0, 0), (0, 0, 0), (1, 1, 1), "bob", window)

ground = engine.FrogObject("Untitled.obj", (0, -2, 0), (0, 0, 0), (5, 1, 5), "bosb", window)

test_object.attach_script("scripts/main.py")
test_object.run_script(variables, "__setup__")

key_map = "wasd"

while window.Bro_Running:
    window.loop()

    keypressed = ""
    for k in key_map:
        if FLAMEACID.has_pressed(k):
            keypressed = k
            break

    window.fill_color((0, 0, 0))
    variables = {
            "dt": 1,
            "self": ["i am an self"],
            "keypressed": keypressed,
            "mouse_pos": FLAMEACID.get_mouse_pos(),
        }
    test_object.run_script(variables, "__tick__")

    camera.run_script(variables, "__tick__")

    test_object.render()
    uniforms = {"u_color": (1, 0, 1)}
    ground.render(uniforms)

    window.update()