import numpy as np


def points(ref):
    import numpy as np

    if ref == "interval":
        return np.array([[i / 20] for i in range(21)])

    if ref == "quadrilateral":
        return np.array([[i / 15, j / 15] for i in range(16) for j in range(16)])
    if ref == "triangle":
        return np.array([[i / 15, j / 15] for i in range(16) for j in range(16 - i)])

    if ref == "hexahedron":
        return np.array([[i / 10, j / 10, k / 10]
                         for i in range(11) for j in range(11) for k in range(11)])
    if ref == "tetrahedron":
        return np.array([[i / 10, j / 10, k / 10]
                         for i in range(11) for j in range(11 - i) for k in range(11 - i - j)])
    if ref == "prism":
        return np.array([[i / 10, j / 10, k / 10]
                         for i in range(11) for j in range(11 - i) for k in range(11)])
    if ref == "pyramid":
        return np.array([[i / 10, j / 10, k / 10]
                         for i in range(11) for j in range(11) for k in range(11 - max(i, j))])

    raise ValueError(f"Unsupported cell type: {ref}")


def same_span(table0, table1):
    if table0.shape != table1.shape:
        return False

    ndofs = table0.shape[-1]
    table0 = table0.reshape(-1, ndofs).T
    table1 = table1.reshape(-1, ndofs).T

    stack = np.vstack([table0, table1])
    rank = np.linalg.matrix_rank(stack)
    return rank == ndofs


def verify(ref, info0, info1):
    edofs0, tab0 = info0
    edofs1, tab1 = info1

    # Check the same number of entity DOFs
    if len(edofs0) != len(edofs1):
        return False
    for i0, i1 in zip(edofs0, edofs1):
        if len(i0) != len(i1):
            return False
        for j0, j1 in zip(i0, i1):
            if len(j0) != len(j1):
                return False

    pts = points(ref)
    table0 = tab0(pts)
    table1 = tab1(pts)

    if table0.shape != table1.shape:
        return False

    if not same_span(table0, table1):
        return False

    return True
