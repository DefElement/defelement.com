"""Symbols used on DefElement."""

reference = "R"
polyset = "\\mathcal{V}"
dual_basis = "\\mathcal{L}"
functional = "l"
basis_function = "\\phi"
vector_basis_function = "\\boldsymbol{\\phi}"
matrix_basis_function = "\\mathbf{\\Phi}"
jacobian = "\\mathbf{J}"
mapping = "\\mathcal{F}"
geometry_map = "F"
transpose = "^{\\text{t}}"


def entity(dim: int) -> str:
    """Get the identifier of an entity.

    Args:
        dim: The entity dimension

    Returns:
        The identifier
    """
    if dim == 0:
        return "v"
    if dim == 1:
        return "e"
    if dim == 2:
        return "f"
    if dim == 3:
        return "c"
    raise ValueError(f"Unsupported dim: {dim}")
