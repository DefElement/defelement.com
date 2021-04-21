import pytest
import os
import yaml
from builder.snippets import symfem_example, basix_example
from builder.element import Categoriser

element_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../elements")
c = Categoriser()
c.load_folder(element_path)

elements = [e.name for e in c.elements]


@pytest.mark.parametrize("element", elements)
@pytest.mark.parametrize("library", ["symfem", "basix"])
def test_snippets(element, library):
    e = c.get_element(element)

    if not e.implemented(library):
        pytest.skip()

    code = e.make_implementation_examples(library)
    exec(code)
