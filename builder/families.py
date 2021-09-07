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


def cockburn_fu_name(family, r="r", cell=None, degree="k"):
    out = ""
    if r != "r":
        out += "\\left["
    out += f"S_{{{family},{degree}}}"
    if cell is not None:
        if cell == "simplex":
            out += "^\\unicode{0x25FA}"
        elif cell == "tp":
            out += "^\\square"
        else:
            raise ValueError(f"Unknown cell: {cell}")
    if r != "r":
        out += f"\\right]_{{{r}}}"
    return out


arnold_logg_reference = {
    "title": "Periodic table of the finite elements",
    "author": "Arnold, D. and Logg, A.",
    "journal": "SIAM News",
    "year": "2014",
    "volume": "47",
    "number": "9",
    "url": "https://sinews.siam.org/Details-Page/periodic-table-of-the-finite-elements"
}

cockburn_fu_reference = {
    "title": "A systematic construction of finite element commuting exact sequences",
    "author": "Cockburn, B. and Fu, G.",
    "journal": "SIAM journal on numerical analysis",
    "volume": "55",
    "number": "4",
    "pagestart": "1650",
    "pageend": "1688",
    "year": "2017",
    "doi": "10.1137/16M1073352"
}
