import pytest
import os
from defelement.element import Categoriser
from defelement.implementations import examples

dir = os.path.dirname(os.path.realpath(__file__))
c = Categoriser()
c.load_categories(os.path.join(dir, "../data/categories"))
c.load_references(os.path.join(dir, "../data/references"))
c.load_folder(os.path.join(dir, "../elements"))

elements = [e.name for e in c.elements]


@pytest.mark.parametrize("element", elements)
@pytest.mark.parametrize("library", examples.keys())
def test_snippets(element, library):
    e = c.get_element(element)

    if not e.implemented(library):
        pytest.skip()

    code = e.make_implementation_examples(library)
    lines = code.split("\n")
    for i, j in enumerate(lines):
        print(j)
        exec("\n".join(lines[:i+1]))

    exec(code)
