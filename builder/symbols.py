reference = "R"
polyset = "\\mathcal{V}"
dual_basis = "\\mathcal{L}"
functional = "l"
basis_function = "\\phi"


def entity(dim):
    if dim == 0:
        return "v"
    if dim == 1:
        return "e"
    if dim == 2:
        return "f"
    if dim == 3:
        return "i"
