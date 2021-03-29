def symfem_example(data):
    out = "import symfem"
    for ref in data["reference elements"]:
        if "min-order" in data:
            if isinstance(data["min-order"], dict):
                min_o = data["min-order"][ref]
            else:
                min_o = data["min-order"]
        else:
            min_o = 0
        max_o = min_o + 2
        if "max-order" in data:
            if isinstance(data["max-order"], dict):
                max_o = min(data["max-order"][ref], max_o)
            else:
                max_o = min(data["max-order"], max_o)

        if data["name"] == "Radau":
            max_o = min(2, max_o)

        for ord in range(min_o, max_o + 1):
            out += "\n\n"
            out += f"# Create {data['name']} order {ord} on a {ref}\n"
            if ref == "dual polygon":
                out += f"element = symfem.create_element(\"{ref}(4)\","
            else:
                out += f"element = symfem.create_element(\"{ref}\","
            if "variant=" in data["symfem"]:
                e_name, variant = data["symfem"].split(" variant=")
                out += f" \"{e_name}\", {ord}, \"{variant}\")"
            else:
                out += f" \"{data['symfem']}\", {ord})"
    return out


def basix_example(data):
    out = "import basix"
    for ref in data["reference elements"]:
        if "min-order" in data:
            if isinstance(data["min-order"], dict):
                min_o = data["min-order"][ref]
            else:
                min_o = data["min-order"]
        else:
            min_o = 0

        if data["name"] == "Lagrange":
            min_o = 1

        max_o = min_o + 2
        if "max-order" in data:
            if isinstance(data["max-order"], dict):
                max_o = min(data["max-order"][ref], max_o)
            else:
                max_o = min(data["max-order"], max_o)
        for ord in range(min_o, max_o + 1):
            out += "\n\n"
            out += f"# Create {data['name']} order {ord} on a {ref}\n"
            out += f"element = basix.create_element("
            if "variant=" in data["basix"]:
                raise NotImplementedError()
            else:
                out += f"\"{data['basix']}\", \"{ref}\", {ord})"
    return out
