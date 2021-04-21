def symfem_example(element):
    out = "import symfem"
    for ref in element.data["reference elements"]:
        min_o = element.min_order(ref)
        max_o = element.max_order(ref)
        if max_o is None:
            max_o = min_o + 2
        else:
            max_o = min(max_o, min_o + 2)

        if element.name == "Radau":
            max_o = min(2, max_o)

        symfem_name, variant = element.get_implementation_string("symfem", ref)

        for ord in range(min_o, max_o + 1):
            out += "\n\n"
            out += f"# Create {element.name} order {ord} on a {ref}\n"
            if ref == "dual polygon":
                out += f"element = symfem.create_element(\"{ref}(4)\","
            else:
                out += f"element = symfem.create_element(\"{ref}\","
            if variant is None:
                out += f" \"{symfem_name}\", {ord})"
            else:
                out += f" \"{symfem_name}\", {ord}, \"{variant}\")"
    return out


def basix_example(element):
    out = "import basix"
    for ref in element.data["reference elements"]:
        min_o = element.min_order(ref)
        max_o = element.max_order(ref)
        if max_o is None:
            max_o = min_o + 2
        else:
            max_o = min(max_o, min_o + 2)

        basix_name, variant = element.get_implementation_string("basix", ref)
        assert variant is None

        for ord in range(min_o, max_o + 1):
            out += "\n\n"
            out += f"# Create {element.name} order {ord} on a {ref}\n"
            out += f"element = basix.create_element("
            out += f"\"{basix_name}\", \"{ref}\", {ord})"
    return out
