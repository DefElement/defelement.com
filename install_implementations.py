import argparse
import os
import yaml
from builder import implementations

parser = argparse.ArgumentParser(description="Install implementations")
parser.add_argument('--install-type', metavar="itype", default="all",
                    help="Type of installation.")
args = parser.parse_args()

with open("data/implementations") as f:
    data = yaml.load(f)

if args.itype == "all":
    for i in data.values():
        os.system(i["install"])
elif args.itype == "verification":
    for i in implemenations.verifications:
        os.system(data[i]["install"])
else:
    raise RuntimeError(f"Unknown install type: {args.itype}")
