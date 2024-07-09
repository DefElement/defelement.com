"""Install all supported implementations."""

import argparse
import os

import yaml

from defelement import implementations

parser = argparse.ArgumentParser(description="Install implementations")
parser.add_argument('--install-type', default="all",
                    help="Type of installation.")
args = parser.parse_args()

with open("data/implementations") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

if args.install_type == "all":
    for i in data.values():
        assert os.system(i["install"]) == 0
elif args.install_type == "verification":
    for i in implementations.verifications:
        assert os.system(data[i]["install"]) == 0
else:
    raise RuntimeError(f"Unknown install type: {args.install_type}")
