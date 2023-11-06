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
        os.system(i["install"])
elif args.install_type == "verification":
    for i in implementations.verifications:
        os.system(data[i]["install"])
else:
    raise RuntimeError(f"Unknown install type: {args.install_type}")
