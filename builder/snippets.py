import re


def _parse_value(v):
    v = v.strip()
    if v[0] == "[" and v[-1] == "]":
        return [_parse_value(i) for i in v[1:-1].split(";")]
    if re.match(r"[0-9]+$", v):
        return int(v)
    return v


def parse_example(e):
    if " {" in e:
        e, rest = e.split(" {")
        rest = rest.split("}")[0]
        while re.search(r"\[([^\]]*),", rest):
            rest = re.sub(r"\[([^\]]*),", r"[\1;", rest)
        kwargs = {}
        for i in rest.split(","):
            key, value = i.split("=")
            kwargs[key] = _parse_value(value)
    else:
        kwargs = {}
    ref, order = e.split(",")
    return ref, int(order), kwargs


def symfem_example(element):
    out = "import symfem"
    for e in element.examples:
        ref, ord, kwargs = parse_example(e)
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
                out += f" \"{symfem_name}\", {ord}, variant=\"{params['variant']}\""
            else:
                out += f" \"{symfem_name}\", {ord}"
            for i, j in kwargs.items():
                if isinstance(j, str):
                    out += f", {i}=\"{j}\""
                else:
                    out += f", {i}={j}"
            out += ")"
    return out


def basix_example(element):
    out = "import basix"
    for e in element.examples:
        ref, ord, kwargs = parse_example(e)
        assert len(kwargs) == 0
        ord = int(ord)

        basix_name, params = element.get_implementation_string("basix", ref)

        if basix_name is not None:
            out += "\n\n"
            out += f"# Create {element.name} order {ord} on a {ref}\n"
            out += "element = basix.create_element("
            out += f"basix.ElementFamily.{basix_name}, basix.CellType.{ref}, {ord}"
            if "lattice" in params:
                out += f", basix.LatticeType.{params['lattice']}"
            if "discontinuous" in params:
                if params["discontinuous"]:
                    out += ", true"
                else:
                    out += ", false"
            out += ")"
    return out


def ufl_example(element):
    out = "import ufl"
    for e in element.examples:
        ref, ord, kwargs = parse_example(e)
        assert len(kwargs) == 0
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


def bempp_example(element):
    out = "import bempp.api"
    out += "\n"
    out += "grid = bempp.api.shapes.regular_sphere(1)"
    for e in element.examples:
        ref, ord, kwargs = parse_example(e)
        assert len(kwargs) == 0
        ord = int(ord)

        bempp_name, params = element.get_implementation_string("bempp", ref)
        if bempp_name is None:
            continue
        orders = [int(i) for i in params["orders"].split(",")]

        if ord in orders:
            out += "\n\n"
            out += f"# Create {element.name} order {ord}\n"
            out += "element = bempp.api.function_space(grid, "
            out += f"\"{bempp_name}\", {ord})"
    return out
