import os
import json
import argparse
import numpy as np
from datetime import datetime
from builder import settings
from builder.element import Categoriser
from builder.implementations import verifications

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
    remaining = [i for i, _ in enumerate(table1)]
    for t0 in table0:
        for i in remaining:
            if np.allclose(t0, table1[i]):
                remaining.remove(i)
                break
        else:
            return False
    return True


def verify(egs, process="", result_dict=None):
    green = "\033[32m"
    red = "\033[31m"
    default = "\033[0m"

    results = {}
    for e, eg, implementations in egs:
        tables = {}
        for i in implementations:
            try:
                tables[i] = verifications[i](e, eg)
            except ImportError:
                print(f"{process}{i} not installed")
            except NotImplementedError:
                pass
        if len(tables) > 0:
            sym_table = verifications["symfem"](e, eg)
            for i, t in tables.items():
                if e.filename not in results:
                    results[e.filename] = {}
                if i not in results[e.filename]:
                    results[e.filename][i] = {"pass": [], "fail": []}
                if sym_table.shape == t.shape and allclose_maybe_permuted(sym_table, t):
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
