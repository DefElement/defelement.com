"""Implementations."""

import importlib
import os
from inspect import isclass

from defelement.implementations.template import Implementation, VariantNotImplemented, parse_example

implementations = []
this_dir = os.path.dirname(os.path.realpath(__file__))
for file in os.listdir(this_dir):
    if file.endswith(".py") and not file.startswith("_") and file != "template.py":
        mod = importlib.import_module(f"defelement.implementations.{file[:-3]}")
        for name in dir(mod):
            if not name.startswith("_"):
                c = getattr(mod, name)
                if isclass(c) and c != Implementation and issubclass(c, Implementation):
                    implementations.append(c)

formats = {i.name: i.format for i in implementations if i.name is not None}
examples = {i.name: i.example for i in implementations if i.name is not None}
verifications = {i.name: i.verify for i in implementations if i.verification and i.name is not None}
