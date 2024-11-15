"""Perform verification checks."""

import argparse
import json
import os
import typing
from datetime import datetime

from defelement import settings
from defelement.element import Categoriser, Element
from defelement.implementations import verifications
from defelement.verification import verify

start_all = datetime.now()

parser = argparse.ArgumentParser(description="Verify elements")
parser.add_argument('destination', metavar='destination', nargs="?",
                    default=None, help="Name of output json file.")
parser.add_argument('--test', metavar="test", default=None,
                    help="Verify fewer elements.")
parser.add_argument('--processes', metavar="processes", default=None,
                    help="The number of processes to run the verification on.")
parser.add_argument('--skip-missing-libraries', default="true",
                    help="Skip verification if library is not installed.")
parser.add_argument('--print-reasons', default="false",
                    help="Show reasons for failed verification")
parser.add_argument('--impl', metavar="impl", default=None,
                    help="libraries to run verification for")

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
        "serendipity", "taylor-hood", "vector-bubble-enriched-Lagrange", "enriched-galerkin",
        "bernardi-raugel"]
else:
    test_elements = args.test.split(",")
if args.impl is None:
    test_implementations = None
else:
    test_implementations = args.impl.split(",")
skip_missing = args.skip_missing_libraries == "true"
print_reasons = args.print_reasons == "true"

categoriser = Categoriser()
categoriser.load_references(os.path.join(settings.data_path, "references"))
categoriser.load_families(os.path.join(settings.data_path, "families"))

# Load elements from .def files
categoriser.load_folder(settings.element_path)

elements_to_verify = []
for e in categoriser.elements:
    if test_elements is None or e.filename in test_elements:
        for eg in e.examples:
            implementations = [
                i for i in verifications
                if i != "symfem" and e.implemented(i) and (
                    test_implementations is None or i in test_implementations)
            ]
            if len(implementations) > 0:
                elements_to_verify.append((e, eg, implementations))


def verify_examples(
    egs: typing.List[typing.Tuple[Element, str, typing.List[str]]], process: str = "",
    result_dict: typing.Optional[typing.Dict[str, typing.Dict[str, typing.Dict[
        str, typing.Dict[str, typing.List[str]]]]]] = None
) -> typing.Dict[str, typing.Dict[str, typing.Dict[str, typing.List[str]]]]:
    """Verify examples.

    Args:
        egs: Examples
        process: String to print on this process
        result_dict: Dictionary to write results into

    Returns:
        Results
    """
    green = "\033[32m"
    red = "\033[31m"
    blue = "\033[34m"
    default = "\033[0m"

    results: typing.Dict[str, typing.Dict[str, typing.Dict[str, typing.List[str]]]] = {}
    for e, eg, implementations in egs:
        if e.filename not in results:
            results[e.filename] = {
                i: {"pass": [], "fail": [], "not implemented": []}
                for i in implementations
            }
        cell = eg.split(",")[0]

        sym_info = verifications["symfem"](e, eg)
        for i in implementations:
            try:
                vinfo = verifications[i](e, eg)
                v, info = verify(cell, vinfo, sym_info)
                if v:
                    results[e.filename][i]["pass"].append(eg)
                    print(f"{process}{e.filename} {i} {eg} {green}\u2713{default}")
                else:
                    results[e.filename][i]["fail"].append(eg)
                    print(f"{process}{e.filename} {i} {eg} {red}\u2715{default}")
                    if print_reasons:
                        print(f"  {info}")
            except ImportError as err:
                if skip_missing:
                    print(f"{process}{i} not installed")
                else:
                    raise err
            except NotImplementedError:
                results[e.filename][i]["not implemented"].append(eg)
                print(f"{process}{e.filename} {i} {eg} {blue}\u2013{default}")

    if result_dict is not None:
        result_dict[process] = results
    return results


if settings.processes == 1:
    data = verify_examples(elements_to_verify)
else:
    import multiprocessing

    p = settings.processes
    n_egs = len(elements_to_verify)

    jobs = []
    manager = multiprocessing.Manager()
    results = manager.dict()
    for i in range(p):
        process = multiprocessing.Process(
            target=verify_examples,
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
    json.dump({
        "metadata": {"date": datetime.now().strftime("%Y-%m-%d")},
        "verification": data,
    }, f)
