import os
import pytest
import re
import signal
import symfem
import urllib.request
import yaml
import warnings


element_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../elements")

inputs = []
for i in os.listdir(element_path):
    if i.endswith(".def"):
        with open(os.path.join(element_path, i)) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        inputs += [(i, c) for c in data["reference elements"]]


@pytest.mark.parametrize("file, cellname", inputs)
def test_latex(file, cellname):
    with open(os.path.join(element_path, file)) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    if "polynomial set" not in data:
        return

    for i, j in data["polynomial set"].items():
        for k in j.split("&&"):
            k = k.strip()
            if k.startswith("<k>"):
                with open("_temp.tex", "w") as f:
                    f.write("\\documentclass{article}\n\n")
                    f.write("\\usepackage{amsmath}\n")
                    f.write("\\usepackage{amssymb}\n")
                    f.write("\\usepackage{amsfonts}\n")
                    f.write("\n\\begin{document}\n")
                    f.write("\\[\n" + k[4:-1] + "\n\\]")
                    f.write("\\end{document}")
                if os.system("pdflatex -halt-on-error _temp.tex > /dev/null") != 0:
                    assert os.system("pdflatex -halt-on-error _temp.tex") == 0
