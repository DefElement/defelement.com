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


def closure_dofs(
    entity_dofs: typing.List[typing.List[typing.List[int]]],
    ref: str
) -> typing.List[typing.List[typing.List[int]]]:
    """Make lists of DOFs associated with the closure of an entity.

    Args:
        entity_dofs: Lists of DOFs associated with each entity
        ref: Reference cell

    Returns:
        Entity closure DOFs
    """
    r = symfem.create_reference(ref)
    out = [[[] for j in i] for i in entity_dofs]
    for dim in range(r.tdim + 1):
        for e_n, e in enumerate(r.sub_entities(dim)):
            for subdim in range(dim + 1):
                for se_n, se in enumerate(r.sub_entities(subdim)):
                    if all(i in e for i in se):
                        out[dim][e_n] += entity_dofs[subdim][se_n]
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
    return rank == srank


def verify(
    ref: str,
    info0: typing.Tuple[typing.List[typing.List[typing.List[int]]],
                        typing.Callable[[Array], Array]],
    info1: typing.Tuple[typing.List[typing.List[typing.List[int]]],
                        typing.Callable[[Array], Array]],
    printing: bool = False
) -> bool:
    """Run verification.

    Args:
        ref: Reference cell
        info0: Verification info for first implementation
        info1: Verification info for second implementation
        printing: Toggle printing

    Returns:
        True if verification successful, otherwise False
    """
    import numpy as np

    edofs0, tab0 = info0
    edofs1, tab1 = info1

    ecdofs0 = closure_dofs(edofs0, ref)
    ecdofs1 = closure_dofs(edofs1, ref)

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
    epoints = entity_points(ref)
    for d, epoints_d in enumerate(epoints):
        for e, pts in enumerate(epoints_d):
            ed0 = ecdofs0[d][e]
            if len(ed0) > 0:
                ed1 = ecdofs1[d][e]

                not_ed0 = [k for i in ecdofs0 for j in i for k in j if k not in ed0]
                not_ed1 = [k for i in ecdofs1 for j in i for k in j if k not in ed1]
                t0 = tab0(pts)[:, :, not_ed0]
                t1 = tab1(pts)[:, :, not_ed1]
                if not np.allclose(t0, t1) and not same_span(t0, t1, False):
                    if printing:
                        print("  Continuity does not match")
                    return False

    return True
