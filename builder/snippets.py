def symfem_example(element):
    out = "import symfem"
    for e in element.examples:
        ref, ord = e.split(",")
        ord = int(ord)

        symfem_name, variant = element.get_implementation_string("symfem", ref)

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
    for e in element.examples:
        ref, ord = e.split(",")
        ord = int(ord)

        basix_name, variant = element.get_implementation_string("basix", ref)
        assert variant is None

        out += "\n\n"
        out += f"# Create {element.name} order {ord} on a {ref}\n"
        out += f"element = basix.create_element("
        out += f"\"{basix_name}\", \"{ref}\", {ord})"
    return out
