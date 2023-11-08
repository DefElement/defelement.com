import os

import yaml

from defelement.element import Element
from defelement.implementations import verifications
from defelement.verification import verify

dir_path = os.path.dirname(os.path.realpath(__file__))
element_path = os.path.join(dir_path, "../elements")


def test_self():
    with open(os.path.join(element_path, "lagrange.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e = Element(data, "lagrange")

    eg = [i for i in e.examples if "triangle" in i][0]

    info = verifications["symfem"](e, eg)
    assert verify("triangle", info, info)


def test_variant():
    with open(os.path.join(element_path, "lagrange.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e = Element(data, "lagrange")

    eg0, eg1 = [i for i in e.examples if "quadrilateral,1" in i][:2]

    info0 = verifications["symfem"](e, eg0)
    info1 = verifications["symfem"](e, eg1)
    assert verify("quadrilateral", info0, info1)


def test_hermite_vs_lagrange():
    with open(os.path.join(element_path, "lagrange.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e = Element(data, "lagrange")
    eg = [i for i in e.examples if "triangle,3" in i][0]
    info0 = verifications["symfem"](e, eg)

    with open(os.path.join(element_path, "hermite.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e = Element(data, "hermite")
    eg = [i for i in e.examples if "triangle,3" in i][0]
    info1 = verifications["symfem"](e, eg)

    assert not verify("triangle", info0, info1)


def test_verify_bdm_vs_n2():
    with open(os.path.join(element_path, "brezzi-douglas-marini.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e0 = Element(data, "brezzi-douglas-marini")
    with open(os.path.join(element_path, "nedelec2.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e1 = Element(data, "nedelec2")

    eg = [i for i in e0.examples if i in e1.examples and "triangle" in i][0]

    info0 = verifications["symfem"](e0, eg)
    info1 = verifications["symfem"](e1, eg)
    assert not verify("triangle", info0, info1)
