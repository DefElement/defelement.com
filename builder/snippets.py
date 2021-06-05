def symfem_example(element):
    out = "import symfem"
    for e in element.examples:
        ref, ord = e.split(",")
        ord = int(ord)

        symfem_name, params = element.get_implementation_string("symfem", ref)

        if symfem_name is not None:
            out += "\n\n"
            out += f"# Create {element.name} order {ord} on a {ref}\n"
            if ref == "dual polygon":
                out += f"element = symfem.create_element(\"{ref}(4)\","
            else:
                out += f"element = symfem.create_element(\"{ref}\","
            if "variant" in params:
                out += f" \"{symfem_name}\", {ord}, \"{params['variant']}\")"
            else:
                out += f" \"{symfem_name}\", {ord})"
    return out


def basix_example(element):
    out = "import basix"
    for e in element.examples:
        ref, ord = e.split(",")
        ord = int(ord)

        basix_name, params = element.get_implementation_string("basix", ref)

        if basix_name is not None:
            out += "\n\n"
            out += f"# Create {element.name} order {ord} on a {ref}\n"
            out += "element = basix.create_element("
            out += f"\"{basix_name}\", \"{ref}\", {ord})"
    return out


def ufl_example(element):
    out = "import ufl"
    for e in element.examples:
        ref, ord = e.split(",")
        ord = int(ord)

        ufl_name, params = element.get_implementation_string("ufl", ref)

        if ufl_name is not None:
            out += "\n\n"
            out += f"# Create {element.name} order {ord} on a {ref}\n"
            if "type" in params:
                out += f"element = ufl.{params['type']}("
            else:
                out += "element = ufl.FiniteElement("
            out += f"\"{ufl_name}\", \"{ref}\", {ord})"
    return out
