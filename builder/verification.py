import symfem
from .utils import to_array


def points(ref):
    import numpy as np

    if ref == "point":
        return np.array([[0.0]])

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


def entity_points(ref):
    import numpy as np

    r = symfem.create_reference(ref)
    out = []
    for d in range(r.tdim):
        row = []
        for n in range(r.sub_entity_count(d)):
            e = r.sub_entity(d, n)
            epts = points(e.name)
            row.append(np.array([
                to_array(e.origin) + sum(i * to_array(a) for i, a in zip(p, e.axes))
                for p in epts]))
        out.append(row)
    return out

    if ref == "interval":
        return [
            [np.array([[0.0]]), np.array([[1.0]])]
        ]
    if ref == "triangle":
        return [
            [np.array([[0.0, 0.0]]), np.array([[1.0, 0.0]]), np.array()]
        ]

    raise ValueError(f"Unsupported cell type: {ref}")


def same_span(table0, table1, complete=True):
    import numpy as np

    if table0.shape != table1.shape:
        return False

    ndofs = table0.shape[-1]
    table0 = table0.reshape(-1, ndofs).T
    table1 = table1.reshape(-1, ndofs).T

    rank = np.linalg.matrix_rank(table0)
    if complete and rank != ndofs:
        return False

    stack = np.vstack([table0, table1])
    srank = np.linalg.matrix_rank(stack)
    return rank == srank


def verify(ref, info0, info1):
    edofs0, tab0 = info0
    edofs1, tab1 = info1

    # Check the same number of entity DOFs
    if len(edofs0) != len(edofs1):
        return False
    entity_counts = []
    for i0, i1 in zip(edofs0, edofs1):
        if len(i0) != len(i1):
            return False
        entity_counts.append(len(i0))
        for j0, j1 in zip(i0, i1):
            if len(j0) != len(j1):
                return False

    # Check that polysets span the same space
    pts = points(ref)
    table0 = tab0(pts)
    table1 = tab1(pts)

    if table0.shape != table1.shape:
        return False

    if not same_span(table0, table1):
        return False

    # Check that continuity will be the same
    epoints = entity_points(ref)
    for d, epoints_d in enumerate(epoints):
        for e, pts in enumerate(epoints_d):
            ed0 = edofs0[d][e]
            if len(ed0) > 0:
                ed1 = edofs1[d][e]
                t0 = tab0(pts)[:, :, ed0]
                t1 = tab1(pts)[:, :, ed1]
                if not same_span(t0, t1, False):
                    return False

    return True
