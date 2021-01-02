import os
dir_path = os.path.dirname(os.path.realpath(__file__))
element_path = os.path.join(dir_path, "../elements")
pages_path = os.path.join(dir_path, "../pages")


def test_contributung_page():
    with open(os.path.join(element_path, "lagrange.def")) as f:
        lagrange = f.read().strip()

    with open(os.path.join(pages_path, "contributing.md")) as f:
        lagrange_from_html = f.read().split("```")[1].strip()

    assert lagrange == lagrange_from_html
