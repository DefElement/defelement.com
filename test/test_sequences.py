import os
import pytest
import re
import signal
import symfem
import urllib.request
import yaml
import warnings


class TimeOutTheTest(BaseException):
    pass


def handler(signum, frame):
    raise TimeOutTheTest()


def check_formula(formula, seq):
    formula = re.sub(r"([0-9])\(", r"\1*(", str(formula))
    formula = re.sub(r"([0-9])k", r"\1*k", str(formula))
    formula = formula.replace(")(", ")*(")
    formula = formula.replace("k(", "k*(")
    formula = formula.replace("^", "**")
    formula = formula.replace("/", "//")
    if "{cases}" in formula:
        formula = formula.split("\\begin{cases}")[1].split("\\end{cases}")[0]
        formula = [i.split("&") for i in formula.split("\\\\")]
        for i, (j, k) in enumerate(formula):
            if "=" in k:
                formula[i][1] = [int(a) for a in k.split("=")[1].split(",")]
            elif ">=" in k:
                formula[i][1] = [a for a in seq if a >= int(k.split(">=")[1])]
            elif ">" in k:
                formula[i][1] = [a for a in seq if a > int(k.split(">")[1])]
        for k, s in seq.items():
            for i, j in formula:
                if k in j:
                    assert s == eval(i.replace("k", str(k)))
                    break
            else:
                warnings.warn(f"k={k} is not included in this sequence")
    else:
        for k, s in seq.items():
            assert s == eval(formula.replace("k", str(k)))


def is_satisfied(condition, n):
    if condition.startswith("k>="):
        return n >= int(condition[3:])
    if condition.startswith("k<="):
        return n <= int(condition[3:])
    if condition.startswith("k>"):
        return n > int(condition[2:])
    if condition.startswith("k<"):
        return n < int(condition[2:])
    raise ValueError


def check_oeis(oeis, seq):
    if " [" in oeis:
        oeis, condition = oeis.split(" [")
        condition = condition.split("]")[0]
        seq = {i: j for i, j in seq.items() if is_satisfied(condition, i)}
    seq = {i: j for i, j in seq.items() if j > 0}
    with urllib.request.urlopen(f"http://oeis.org/{oeis}/list") as f:
        oeis_seq = "".join([
            i.strip() for i in f.read().decode('utf-8').split(
                "<pre>[")[1].split("]</pre>")[0].split("\n")])
    assert ",".join([str(i) for i in seq.values()]) in oeis_seq


element_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../elements")

inputs = []
for i in os.listdir(element_path):
    if i.endswith(".def"):
        with open(os.path.join(element_path, i)) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        inputs += [(i, c) for c in data["reference elements"]]


@pytest.mark.parametrize("file, cellname", inputs)
def test_sequence(file, cellname):
    if cellname == "dual polygon":
        pytest.skip()
    with open(os.path.join(element_path, file)) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    if "symfem" not in data:
        pytest.skip()
    if "ndofs" not in data and "ndofs-oeis" not in data:
        pytest.skip()

    seq = {}
    if "min-order" in data:
        if isinstance(data["min-order"], dict):
            mink = data["min-order"][cellname]
        else:
            mink = data["min-order"]
    else:
        mink = 0
    maxk = 10
    if "max-order" in data:
        if isinstance(data["max-order"], dict):
            maxk = data["max-order"][cellname]
        else:
            maxk = min(maxk, data["max-order"])
    for k in range(mink, maxk + 1):
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(25)
            if "variant=" in data["symfem"]:
                elementname, variant = data["symfem"].split(" variant=")
                term = len(symfem.create_element(cellname, elementname, k, variant).dofs)
            else:
                term = len(symfem.create_element(cellname, data["symfem"], k).dofs)
            seq[k] = term
        except NotImplementedError:
            pass
        except TimeOutTheTest:
            break

    signal.alarm(0)

    if "ndofs" in data and cellname in data["ndofs"]:
        check_formula(data["ndofs"][cellname], seq)

    if "ndofs-oeis" in data and cellname in data["ndofs-oeis"]:
        check_oeis(data["ndofs-oeis"][cellname], seq)


@pytest.mark.parametrize("file, cellname", inputs)
def test_entity_sequences(file, cellname):
    if cellname == "dual polygon":
        pytest.skip()
    with open(os.path.join(element_path, file)) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    if "symfem" not in data:
        pytest.skip()
    if "entity-ndofs" not in data and "entity-ndofs-oeis" not in data:
        pytest.skip()

    seq = {"vertices": {}, "edges": {}, "faces": {}, "volumes": {},
           "cell": {}, "facets": {}, "ridges": {}, "peaks": {}}
    if "min-order" in data:
        if isinstance(data["min-order"], dict):
            mink = data["min-order"][cellname]
        else:
            mink = data["min-order"]
    else:
        mink = 0
    maxk = 10
    if "max-order" in data:
        if isinstance(data["max-order"], dict):
            maxk = data["max-order"][cellname]
        else:
            maxk = min(maxk, data["max-order"])
    for k in range(mink, maxk + 1):
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(25)
            if "variant=" in data["symfem"]:
                elementname, variant = data["symfem"].split(" variant=")
                e = symfem.create_element(cellname, elementname, k, variant)
            else:
                e = symfem.create_element(cellname, data["symfem"], k)
            for d, e_name in zip(range(e.reference.tdim),
                                 ["vertices", "edges", "faces", "volumes"]):
                seq[e_name][k] = len(e.entity_dofs(d, 0))
            for co_d, e_name in zip(range(e.reference.tdim),
                                          ["cell", "facets", "ridges", "peaks"]):
                seq[e_name][k] = len(e.entity_dofs(e.reference.tdim - co_d, 0))
        except NotImplementedError:
            pass
        except TimeOutTheTest:
            break

    signal.alarm(0)

    if "entity-ndofs" in data:
        for entity in data["entity-ndofs"]:
            check_formula(data["entity-ndofs"][entity], seq[entity])

    if "entity-ndofs-oeis" in data:
        for entity in data["entity-ndofs-oeis"]:
            check_oeis(data["entity-ndofs-oeis"][entity], seq[entity])
