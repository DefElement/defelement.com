"""Install all supported implementations."""

import argparse
import os

from defelement import implementations

parser = argparse.ArgumentParser(description="Install implementations")
parser.add_argument('--install-type', default="all",
                    help="Type of installation.")
args = parser.parse_args()

if args.install_type == "all":
    for i in implementations.implementations.values():
        assert i.install is not None
        assert os.system(i.install) == 0
elif args.install_type == "verification":
    for i in implementations.implementations.values():
        if i.verification:
            assert i.install is not None
            assert os.system(i.install) == 0
else:
    raise RuntimeError(f"Unknown install type: {args.install_type}")
