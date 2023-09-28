import os
import basix
import json
import argparse
import numpy as np
from datetime import datetime
from builder import settings
from builder.element import Categoriser
from builder.implementations import verifications, symfem_create_element


def points(ref):
    import numpy as np

    if ref == "interval":
        return np.array([[i / 15] for i in range(16)])
    if ref == "quadrilateral":
        return np.array([[i / 10, j / 10] for i in range(11) for j in range(11)])
    if ref == "hexahedron":
        return np.array([[i / 6, j / 6, k / 6]
                         for i in range(7) for j in range(7) for k in range(7)])
    if ref == "triangle":
        return np.array([[i / 10, j / 10] for i in range(11) for j in range(11 - i)])
    if ref == "tetrahedron":
        return np.array([[i / 6, j / 6, k / 6]
                         for i in range(7) for j in range(7 - i) for k in range(7 - i - j)])
    if ref == "prism":
        return np.array([[i / 6, j / 6, k / 6]
                         for i in range(7) for j in range(7 - i) for k in range(7)])
    if ref == "pyramid":
        return np.array([[i / 6, j / 6, k / 6]
                         for i in range(7) for j in range(7) for k in range(7 - max(i, j))])

    raise ValueError(f"Unsupported cell type: {ref}")


start_all = datetime.now()

parser = argparse.ArgumentParser(description="Build defelement.com")
parser.add_argument('destination', metavar='destination', nargs="?",
                    default=None, help="Name of output json file.")
parser.add_argument('--test', metavar="test", default=None,
                    help="Verify fewer elements.")
parser.add_argument('--processes', metavar="processes", default=None,
                    help="The number of processes to run the verification on.")

args = parser.parse_args()
if args.destination is not None:
    settings.verification_json = args.destination
if args.processes is not None:
    settings.processes = int(args.processes)
if args.test is None:
    test_elements = None
elif args.test == "auto":
    test_elements = [
        "buffa-christiansen", "direct-serendipity", "dual", "hellan-herrmann-johnson",
        "hsieh-clough-tocher", "lagrange", "nedelec1", "raviart-thomas", "regge",
        "serendipity", "taylor-hood", "vector-bubble-enriched-Lagrange", "enriched-galerkin"]
else:
    test_elements = args.test.split(",")

categoriser = Categoriser()
categoriser.load_references(os.path.join(settings.data_path, "references"))
categoriser.load_families(os.path.join(settings.data_path, "families"))

# Load elements from .def files
categoriser.load_folder(settings.element_path)

elements_to_verify = []
for e in categoriser.elements:
    if test_elements is None or e.filename in test_elements:
        for eg in e.examples:
            implementations = [i for i in verifications if i != "symfem" and e.implemented(i)]
            if len(implementations) > 0:
                elements_to_verify.append((e, eg, implementations))


def allclose_maybe_permuted(table0, table1):
    remaining = [i for i, _ in enumerate(table1.T)]
    for t0 in table0.T:
        for i in remaining:
            if np.allclose(t0, table1.T[i]):
                remaining.remove(i)
                break
        else:
            return False
    return True


def legendre_coefficients(tabulate, cell, max_degree):
    celltype = getattr(basix.CellType, cell)
    pts, wts = basix.make_quadrature(celltype, max_degree * 2)
    # Evaluate function at quadrature points
    values = tabulate(pts)
    # Evaluate orthogonal basis at quadrature points
    poly = basix.tabulate_polynomials(basix.PolynomialType.legendre, celltype, max_degree, pts)
    # Create matrix
    mat = np.zeros((values.shape[2], poly.shape[0] * values.shape[1]))
    # a_ij = sum_k(w_k function_i(p_k) * legendre_j(p_k))
    for i in range(values.shape[2]):
        for j in range(poly.shape[0]):
            for v in range(values.shape[1]):
                for k in range(pts.shape[0]):
                    mat[i, j * values.shape[1] + v] += wts[k] * values[k, v, i] * poly[j, k]
    return mat


def verify(egs, process="", result_dict=None):
    green = "\033[32m"
    red = "\033[31m"
    blue = "\033[34m"
    default = "\033[0m"

    results = {}
    for e, eg, implementations in egs:
        symfem_e = symfem_create_element(e, eg)
        max_degree = symfem_e.maximum_degree
        if "pyramid" in eg:
            continue

        tables = {}
        for i in implementations:
            try:
                tables[i] = legendre_coefficients(
                    lambda pts: verifications[i](e, eg, pts),
                    symfem_e.reference.name, max_degree)
            except ImportError:
                print(f"{process}{i} not installed")
            except NotImplementedError:
                if e.filename not in results:
                    results[e.filename] = {}
                if i not in results[e.filename]:
                    results[e.filename][i] = {"pass": [], "fail": [], "not implemented": []}
                results[e.filename][i]["not implemented"].append(eg)
                print(f"{process}{e.filename} {i} {eg} {blue}\u2013{default}")
        if len(tables) > 0:
            sym_table = legendre_coefficients(
                lambda pts: verifications["symfem"](e, eg, pts),
                symfem_e.reference.name, max_degree)
            for i, t in tables.items():
                stack = np.vstack([sym_table, t])
                rank = np.linalg.matrix_rank(stack)
                if e.filename not in results:
                    results[e.filename] = {}
                if i not in results[e.filename]:
                    results[e.filename][i] = {"pass": [], "fail": [], "not implemented": []}
                if rank == sym_table.shape[0]:
                    results[e.filename][i]["pass"].append(eg)
                    print(f"{process}{e.filename} {i} {eg} {green}\u2713{default}")
                else:
                    results[e.filename][i]["fail"].append(eg)
                    print(f"{process}{e.filename} {i} {eg} {red}\u2715{default}")
    if result_dict is not None:
        result_dict[process] = results
    return results


if settings.processes == 1:
    data = verify(elements_to_verify)
else:
    import multiprocessing

    p = settings.processes
    n_egs = len(elements_to_verify)

    jobs = []
    manager = multiprocessing.Manager()
    results = manager.dict()
    for i in range(p):
        process = multiprocessing.Process(
            target=verify,
            args=(elements_to_verify[n_egs * i // p: n_egs * (i + 1) // p], f"[{i}] ", results)
        )
        jobs.append(process)

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()

    for j in jobs:
        assert j.exitcode == 0

    data = {}
    for r in results.values():
        for i0, j0 in r.items():
            if i0 not in data:
                data[i0] = {}
            for i1, j1 in j0.items():
                if i1 not in data[i0]:
                    data[i0][i1] = {}
                for i2, j2 in j1.items():
                    if i2 not in data[i0][i1]:
                        data[i0][i1][i2] = []
                    data[i0][i1][i2] += j2

with open(settings.verification_json, "w") as f:
    json.dump(data, f)
