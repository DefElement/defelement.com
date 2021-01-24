import os
import pytest
import re
import signal
import symfem
import urllib.request
import yaml


class TimeOutTheTest(BaseException):
    pass


def handler(signum, frame):
    raise TimeOutTheTest()


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
            term = len(symfem.create_element(cellname, data["symfem"], k).dofs)
            seq[k] = term
        except NotImplementedError:
            pass
        except TimeOutTheTest:
            break

    if "ndofs" in data and cellname in data["ndofs"]:
        formula = data["ndofs"][cellname]

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
                    formula[i][1] = [a for a in seq if a >= int(k.split(">")[1])]
            for k, s in seq.items():
                for i, j in formula:
                    if k in j:
                        assert s == eval(i.replace("k", str(k)))
                        break
                else:
                    raise ValueError
        else:
            for k, s in seq.items():
                assert s == eval(formula.replace("k", str(k)))

    if "ndofs-oeis" in data and cellname in data["ndofs-oeis"]:
        oeis = data["ndofs-oeis"][cellname]
        with urllib.request.urlopen(f"http://oeis.org/{oeis}/list") as f:
            oeis_seq = "".join([
                i.strip() for i in f.read().decode('utf-8').split(
                    "<pre>[")[1].split("]</pre>")[0].split("\n")])
        assert ",".join([str(i) for i in seq.values()]) in oeis_seq
