"""Implementations."""

import importlib
import os
from inspect import isclass

from defelement.implementations.core import (
    DegreeNotImplemented, Implementation, NotImplementedOnReference,
    VariantNotImplemented, parse_example)

implementations = {}
this_dir = os.path.dirname(os.path.realpath(__file__))
for file in os.listdir(this_dir):
    if file.endswith(".py") and not file.startswith("_") and file != "core.py":
        mod = importlib.import_module(f"defelement.implementations.{file[:-3]}")
        for name in dir(mod):
            if not name.startswith("_"):
                c = getattr(mod, name)
                if isclass(c) and c != Implementation and issubclass(c, Implementation):
                    assert c.id is not None
                    implementations[c.id] = c

formats = {id: i.format for id, i in implementations.items()}
examples = {id: i.example for id, i in implementations.items()}
verifications = {id: i.verify for id, i in implementations.items() if i.verification}
