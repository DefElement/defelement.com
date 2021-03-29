import os
import pytest
import re
import signal
import symfem
import urllib.request
import yaml
from builder.snippets import symfem_example, basix_example


class TimeOutTheTest(BaseException):
    pass


def handler(signum, frame):
    raise TimeOutTheTest()


element_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../elements")

files = []
for i in os.listdir(element_path):
    if i.endswith(".def"):
        files.append(i)


@pytest.mark.parametrize("file", files)
def test_symfem_snippet(file):
    with open(os.path.join(element_path, file)) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    if "symfem" not in data:
        pytest.skip()

    code = symfem_example(data)
    exec(code)


@pytest.mark.parametrize("file", files)
def test_basix_snippet(file):
    with open(os.path.join(element_path, file)) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    print(data)

    if "basix" not in data:
        pytest.skip()

    code = basix_example(data)
    exec(code)
