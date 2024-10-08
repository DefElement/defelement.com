"""Element families."""

import typing


def arnold_logg_name(
    family: str, r: str = "r", cell: typing.Optional[str] = None, degree: str = "k", dim: str = "d"
) -> str:
    """Get the name used in the Periodic Table of Finite Elements.

    Args:
        family: Family
        r: Exterior derivative order
        cell: Cell type
        degree: Polynomial degree
        dim: Cell dimension

    Returns:
        Formatted name
    """
    out = f"\\mathcal{{{family[0]}}}"
    if len(family) > 1:
        out += f"^{family[1]}"
    out += f"_{{{degree}}}"
    out += f"\\Lambda^{{{r}}}"
    if cell is not None:
        if cell == "simplex":
            out += f"(\\Delta_{dim})"
        elif cell == "tp":
            out += f"(\\square_{dim})"
        else:
            raise ValueError(f"Unknown cell: {cell}")
    return out


def cockburn_fu_name(
    family: str, r: str = "r", cell: typing.Optional[str] = None, degree: str = "k", dim: str = "d"
) -> str:
    """Get the name used in the Cockburn-Fu paper.

    Args:
        family: Family
        r: Exterior derivative order
        cell: Cell type
        degree: Polynomial degree
        dim: Cell dimension

    Returns:
        Formatted name
    """
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


def custom_name(
    family: str, r: str = "r", cell: typing.Optional[str] = None, degree: str = "k", dim: str = "d"
):
    """Get a custom name.

    Args:
        family: Family
        r: Exterior derivative order
        cell: Cell type
        degree: Polynomial degree
        dim: Cell dimension

    Returns:
        Formatted name
    """
    out = family
    if isinstance(family, dict):
        if r == "r":
            out = family["general"]
        else:
            out = family[r]
    out = out.replace("<r>", f"{r}")
    out = out.replace("<dim>", f"{dim}")
    out = out.replace("<degree>", f"{degree}")
    return out


arnold_logg_reference = {
    "title": "Periodic table of the finite elements",
    "author": "Arnold, Douglas N. and Logg, Anders",
    "journal": "SIAM News",
    "year": "2014",
    "volume": "47",
    "number": "9",
    "url": "https://www.siam.org/publications/siam-news/issues/volume-47-number-09-november-2014/"
}

cockburn_fu_reference = {
    "title": "A systematic construction of finite element commuting exact sequences",
    "author": "Cockburn, Bernardo and Fu, Guosheng",
    "journal": "SIAM journal on numerical analysis",
    "volume": "55",
    "number": "4",
    "pagestart": "1650",
    "pageend": "1688",
    "year": "2017",
    "doi": "10.1137/16M1073352"
}

keys_and_names = [
    ("cockburn-fu", cockburn_fu_name),
    ("arnold-logg", arnold_logg_name),
    ("name", custom_name),
]
