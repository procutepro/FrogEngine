import dis
import FLAMEACID


# ------------------------------
# 1. Bytecode extraction & compilation
# ------------------------------

def extract_instructions(file_name):
    with open(file_name) as f:
        code = compile(f.read(), file_name, "exec")
    return list(dis.get_instructions(code))


def build_offset_map(instructions):
    return {instr.offset: idx for idx, instr in enumerate(instructions)}


def compile_actions(variables, instructions):
    variables = variables.copy()
    actions = []
    stack = []
    compare_result = False
    offset_to_index = build_offset_map(instructions)

    i = 0
    while i < len(instructions):
        instr = instructions[i]
        op = instr.opname
        arg = instr.argval

        # Comparison
        if op == "COMPARE_OP":
            b, a = stack.pop(), stack.pop()
            compare_result = {
                "==": a == b,
                "<": a < b,
                ">": a > b
            }.get(arg, False)

        # Jump
        elif op == "POP_JUMP_IF_FALSE" and not compare_result:
            i = offset_to_index[arg] - 1
            compare_result = False

        # Pop
        elif op == "POP_TOP" and stack:
            stack.pop()

        # Load constants
        elif op == "LOAD_CONST":
            stack.append(arg)

        # Store
        elif op in ("STORE_NAME", "STORE_FAST"):
            variables[arg] = stack.pop()

        # Store attribute
        elif op == "STORE_ATTR":
            value = stack[-2]
            actions.append({"do_thing": "add_val", "params": (arg, value)})
            variables[arg] = value
            del stack[-2]

        # Load variable
        elif op in ("LOAD_FAST", "LOAD_GLOBAL", "LOAD_FAST_CHECK"):
            if arg == "self":
                stack.append(variables.get("self", "self"))
            else:
                stack.append(variables.get(arg))

        elif op == "BUILD_LIST":
            stack.append(stack)

        elif op == "BINARY_SUBSCR":
            index = stack.pop()
            lsut = stack.pop()
            stack.append(lsut[index])

        # Load attribute
        elif op == "LOAD_ATTR":
            stack.append(arg)

        # Operations
        elif op == "UNARY_NEGATIVE":
            thing = stack.pop()
            stack.append(-thing)

        elif op == "BINARY_OP":
            b = stack.pop()
            a = stack.pop()

            operation_map = {
                0: "+",
                5: "*",
                10: "-",
                11: "/",
            }

            if operation_map[arg] == "+":
                stack.append(a + b)
            if operation_map[arg] == "-":
                stack.append(a - b)
            if operation_map[arg] == "*":
                stack.append(a * b)
            if operation_map[arg] == "/":
                stack.append(a / b)

        # Call function/method
        elif op == "CALL":
            num_args = arg
            args = [stack.pop() for _ in range(num_args)]
            func_name = stack.pop()
            self_obj = stack.pop()

            if self_obj in ("self", ["i am an self"]) or "Self" in self_obj:
                actions.append({
                    "do_thing": "run_func",
                    "params": (func_name, args[::-1])
                })
            else:
                print(f"Warning: CALL on non-self object: {self_obj}")

        i += 1

    return actions


# ------------------------------
# 2. Function extraction from bytecode
# ------------------------------

def extract_functions(instructions):
    functions = {}
    i = 0
    while i < len(instructions):
        if instructions[i].opname == "MAKE_FUNCTION":
            func = instructions[i - 1].argval
            functions[func.co_name] = list(dis.get_instructions(func))
        i += 1
    return functions


if __name__ == "__main__":
    # ------------------------------
    # 3. Main setup
    # ------------------------------
    
    instructions = extract_instructions("scripts/main.py")
    functions = extract_functions(instructions)
    
    setup_instructions = functions["__setup__"]
    tick_instructions = functions["__tick__"]
    
    initial_vars = {"dt": 60, "self": ["i am an self"], "keypressed": "a"}
    start_actions = compile_actions(initial_vars, setup_instructions)
    
    self_vars = {}
    for action in start_actions:
        if action["do_thing"] == "add_val":
            self_vars[action["params"][0]] = action["params"][1]
    
    # ------------------------------
    # 4. Engine setup (FLAMEACID)
    # ------------------------------
    
    window = FLAMEACID.Window3D((800, 600), "test")
    camera = FLAMEACID.Camera(pos=(5, 5, 5), target=(0, 0, 0))
    window.set_camera(camera)
    
    mesh = FLAMEACID.Mesh(
        "Untitled.obj",
        (0, 0, 0),
        (1, 1, 1),
        (0, 0, 0),
        window,
        "default",
        use_texture="color"
    )
    mesh.init()
    
    # ------------------------------
    # 5. Game loop
    # ------------------------------
    
    key_map = {
        "w": (0.01, 0, 0),
        "s": (-0.01, 0, 0),
        "a": (0, 0, 0.01),
        "d": (0, 0, -0.01),
    }
    
    while window.Bro_Running:
        window.loop()
        window.fill_color((0, 0, 0))
    
        # Input
        keypressed = ""
        for k in key_map:
            if FLAMEACID.has_pressed(k):
                keypressed = k
                break
            
        # Build VM state
        variables = {
            "dt": 1,
            "self": ["i am an self"],
            "keypressed": keypressed,
            **self_vars
        }
    
        # Run VM
        actions = compile_actions(variables, tick_instructions)
    
        # Execute actions
        for action in actions:
            if action["do_thing"] == "add_val":
                key, val = action["params"]
                self_vars[key] = val
    
            elif action["do_thing"] == "run_func" and action["params"][0] == "move":
                dx, dy, dz, _ = action["params"][1]
                mesh.pos[0] += dx
                mesh.pos[1] += dy
                mesh.pos[2] += dz
                mesh.get_model_matrix()
    
        mesh.render()
        window.update()