def symfem_example(element):
    out = "import symfem"
    for ref in element.data["reference elements"]:
        if "min-order" in element.data:
            if isinstance(element.data["min-order"], dict):
                min_o = element.data["min-order"][ref]
            else:
                min_o = element.data["min-order"]
        else:
            min_o = 0
        max_o = min_o + 2
        if "max-order" in element.data:
            if isinstance(element.data["max-order"], dict):
                max_o = min(element.data["max-order"][ref], max_o)
            else:
                max_o = min(element.data["max-order"], max_o)

        if element.data["name"] == "Radau":
            max_o = min(2, max_o)

        if isinstance(element.data["symfem"], dict):
            symfem_name = element.data["symfem"][ref]
        else:
            symfem_name = element.data["symfem"]
        for ord in range(min_o, max_o + 1):
            out += "\n\n"
            out += f"# Create {element.data['name']} order {ord} on a {ref}\n"
            if ref == "dual polygon":
                out += f"element = symfem.create_element(\"{ref}(4)\","
            else:
                out += f"element = symfem.create_element(\"{ref}\","
            if "variant=" in symfem_name:
                e_name, variant = symfem_name.split(" variant=")
                out += f" \"{e_name}\", {ord}, \"{variant}\")"
            else:
                out += f" \"{symfem_name}\", {ord})"
    return out


def basix_example(element):
    out = "import basix"
    for ref in element.data["reference elements"]:
        if "min-order" in element.data:
            if isinstance(element.data["min-order"], dict):
                min_o = element.data["min-order"][ref]
            else:
                min_o = element.data["min-order"]
        else:
            min_o = 0

        if element.data["name"] == "Lagrange":
            min_o = 1

        max_o = min_o + 2
        if "max-order" in element.data:
            if isinstance(element.data["max-order"], dict):
                max_o = min(element.data["max-order"][ref], max_o)
            else:
                max_o = min(element.data["max-order"], max_o)
        for ord in range(min_o, max_o + 1):
            out += "\n\n"
            out += f"# Create {element.data['name']} order {ord} on a {ref}\n"
            out += f"element = basix.create_element("
            if "variant=" in element.data["basix"]:
                raise NotImplementedError()
            else:
                out += f"\"{element.data['basix']}\", \"{ref}\", {ord})"
    return out
