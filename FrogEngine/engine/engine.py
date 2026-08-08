import interperter as interperter
import FLAMEACID

class FrogBase:
    def __init__(self, pos, rot, name):
        self.pos = list(pos)
        self.rot = list(rot)
        self.name = name
        self.self_vars = {}
        self.script_data = {
            "__setup__": ...,
            "__tick__": ...,
        }

    def attach_script(self, script_path):
        instructions = interperter.extract_instructions(script_path)
        scripts = interperter.extract_functions(instructions)

        self.script_data["__setup__"] = scripts["__setup__"]
        self.script_data["__tick__"] = scripts["__tick__"]

    def move(self, delta):
        self.pos[0] += delta[0]
        self.pos[1] += delta[1]
        self.pos[2] += delta[2]
        self.update()

    def rotate(self, delta):
        self.rot[0] += delta[0]
        self.rot[1] += delta[1]
        self.rot[2] += delta[2]
        self.update()

    def run_actions(self, actions):
        for action in actions:
            if action["do_thing"] == "add_val":
                key, val = action["params"]
                self.self_vars[key] = val
    
            elif action["do_thing"] == "run_func":
                if action["params"][0] == "move":
                    self.move(action["params"][1][0:3])

                if action["params"][0] == "rotate":
                    self.rotate(action["params"][1][0:3])

    def update(self): ...

    def render(self, uniforms): ...

class Camera(FrogBase):
    def __init__(self, pos, rot, name):
        super().__init__(pos, rot, name)
        self.camera_obj = FLAMEACID.Camera(pos=pos, target=rot)
        self.camera_obj.look_in_direction(rot)

    def __call__(self):
        return self.camera_obj

    def update(self):
        self.camera_obj.update_matrix()

    def move(self, delta):

        self.pos[0] += delta[0]
        self.pos[1] += delta[1]
        self.pos[2] += delta[2]

        self.camera_obj.pos[0] += delta[0]
        self.camera_obj.pos[1] += delta[1]
        self.camera_obj.pos[2] += delta[2]

        self.camera_obj.target[0] += delta[0]
        self.camera_obj.target[1] += delta[1]
        self.camera_obj.target[2] += delta[2]

        self.update()

    def rotate(self, rot):
        self.camera_obj.look_in_direction(rot)

    def run_script(self, variables, script):
            thing_variables = variables.copy()
            thing_variables["self"] = f"Self|Camera|{self.name}"
            actions = interperter.compile_actions(thing_variables, self.script_data[script])
            self.run_actions(actions)

class FrogObject(FrogBase):
    def __init__(self, model_path, pos, rot, size, name, window):
        super().__init__(pos, rot, name)
        self.size = size
        model = FLAMEACID.obj.load_obj(model_path)
        self.triangles = []
        for tri in model:
            self.triangles.extend(tri)

        self.mesh = FLAMEACID.Mesh(model_path, pos, size, rot, window, "default", use_texture="color")

    def move(self, delta):
        super().move(delta)
        self.mesh.pos[0] = self.pos[0]
        self.mesh.pos[1] = self.pos[1]
        self.mesh.pos[2] = self.pos[2]
        self.mesh.get_model_matrix()

    def rotate(self, rot):
        super().rotate(rot)
        self.mesh.rotation = self.rot
        self.mesh.get_model_matrix()

    def render(self, uniforms=None):
        self.mesh.render(uniforms)

    def run_script(self, variables, script):
            thing_variables = variables.copy()
            thing_variables["self"] = f"Self|Model|{self.name}"
            actions = interperter.compile_actions(thing_variables, self.script_data[script])
            self.run_actions(actions)