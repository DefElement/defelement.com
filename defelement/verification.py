"""Verification."""

import typing

import symfem

from defelement.tools import to_array

if typing.TYPE_CHECKING:
    from numpy import float64
    from numpy.typing import NDArray
    Array = NDArray[float64]
else:
    Array = typing.Any


def points(ref: str) -> Array:
    """Get tabulation points for a reference cell.

    Args:
        ref: Reference cell

    Returns:
        Set of points
    """
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


def entity_points(ref: str) -> typing.List[typing.List[Array]]:
    """Get tabulation points for sub-entities of a reference cell.

    Args:
        ref: Reference cell

    Returns:
        Set of points
    """
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


def entity_quadrature_rules(ref: str, degree: int) -> typing.List[typing.List[typing.Tuple[Array, Array]]]:
    """Get quadrature rules for sub-entities of a reference cell.

    Args:
        ref: Reference cell

    Returns:
        Set of points
    """
    import numpy as np
    import basix

    r = symfem.create_reference(ref)
    out = []
    for d in range(r.tdim):
        row = []
        for n in range(r.sub_entity_count(d)):
            e = r.sub_entity(d, n)
            if e.name == "point":
                pts = np.array([[]])
                wts = np.array([1.0])
            else:
                cell_type = getattr(basix.CellType, e.name)
                pts, wts = basix.make_quadrature(cell_type, degree)
                wts *= float(e.volume() / e.default_reference().volume())
            row.append((np.array([
                to_array(e.origin) + sum(i * to_array(a) for i, a in zip(p, e.axes))
                for p in pts
            ]), wts))
        out.append(row)
    return out


def same_span(table0: Array, table1: Array, complete: bool = True) -> bool:
    """Check if two tables span the same space.

    Args:
        table0: First table
        table1: Second table
        complete: Should the tables have full rank?

    Returns:
        True if span is the same, otherwise False
    """
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
    print(rank, srank)
    return rank == srank


def verify(
    ref: str,
    info0: typing.Tuple[typing.List[typing.List[typing.List[int]]],
                        typing.Callable[[Array], Array]],
    info1: typing.Tuple[typing.List[typing.List[typing.List[int]]],
                        typing.Callable[[Array], Array]],
    lagrange_superdegree: int,
    printing: bool = False
) -> bool:
    """Run verification.

    Args:
        ref: Reference cell
        info0: Verification info for first implementation
        info1: Verification info for second implementation
        lagrange_superdegree: The Lagrange superdegree of the element
        printing: Toggle printing

    Returns:
        True if verification successful, otherwise False
    """
    import numpy as np

    edofs0, tab0 = info0
    edofs1, tab1 = info1

    # Check the same number of entity DOFs
    if len(edofs0) != len(edofs1):
        if printing:
            print("  Wrong number of entities")
        return False
    entity_counts = []
    for i0, i1 in zip(edofs0, edofs1):
        if len(i0) != len(i1):
            if printing:
                print("  Wrong number of entities")
            return False
        entity_counts.append(len(i0))
        for j0, j1 in zip(i0, i1):
            if len(j0) != len(j1):
                if printing:
                    print("  Wrong number of DOFs associated with an entity")
                return False

    # Check that polysets span the same space
    pts = points(ref)
    table0 = tab0(pts)
    table1 = tab1(pts)

    if table0.shape != table1.shape:
        if printing:
            print("  Non-matching table shapes")
        return False

    if not same_span(table0, table1):
        if printing:
            print("  Polysets do not span the same space")
        return False

    # Check that continuity will be the same
    erules = entity_quadrature_rules(ref, 2 * lagrange_superdegree)
    for d, erules_d in enumerate(erules):
        for e, (pts, wts) in enumerate(erules_d):
            ed0 = edofs0[d][e]
            if len(ed0) > 0:
                ed1 = edofs1[d][e]

                t0 = tab0(pts)
                t0e = t0[:, :, ed0]
                not_ed0 = [k for i in edofs0 for j in i for k in j if k not in ed0]
                t0perp = t0[:, :, not_ed0]
                for i in range(t0e.shape[2]):
                    for j in range(t0perp.shape[2]):
                        t0e[:, :, i] -= ((t0e[:, :, i] * t0perp[:, :, j]).sum(axis=1) * wts).sum() / ((t0perp[:, :, j] * t0perp[:, :, j]).sum(axis=1) * wts).sum() * t0perp[:, :, j]

                t1 = tab1(pts)
                t1e = t1[:, :, ed1]
                not_ed1 = [k for i in edofs1 for j in i for k in j if k not in ed1]
                t1perp = t1[:, :, not_ed1]
                for i in range(t1e.shape[2]):
                    for j in range(t1perp.shape[2]):
                        t1e[:, :, i] -= ((t1e[:, :, i] * t1perp[:, :, j]).sum(axis=1) * wts).sum() / ((t1perp[:, :, j] * t1perp[:, :, j]).sum(axis=1) * wts).sum() * t1perp[:, :, j]

                print(t0)
                print(t1)

                if not np.allclose(t0e, t1e) and not same_span(t0e, t1e, False):
                    if printing:
                        print("  Continuity does not match")
                    return False

    return True
