def arnold_logg_name(family, r="r", cell=None, degree="k"):
    out = f"\\mathcal{{{family[0]}}}"
    if len(family) > 1:
        out += f"^{family[1]}"
    out += f"_{{{degree}}}"
    out += f"\\Lambda^{{{r}}}"
    if cell is not None:
        if cell == "simplex":
            out += "(\\Delta_d)"
        elif cell == "tp":
            out += "(\\square_d)"
        else:
            raise ValueError(f"Unknown cell: {cell}")
    return out


def cockburn_foo_name(family, r="r", cell=None, degree="k"):
    out = ""
    if r != "r":
        out += "\\left["
    out += f"S_{{{family},{degree}}}"
    if cell is not None:
        if cell == "simplex":
            out += "^\\Delta"
        elif cell == "tp":
            out += "^\\square"
        else:
            raise ValueError(f"Unknown cell: {cell}")
    if r != "r":
        out += f"\\right]_{{{r}}}"
    return out
