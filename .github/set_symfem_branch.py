"""Script to update Symfem branch in CI.

For example, to make the tests run using a Symfem branch called "test2", run:
    python3 set_symfem_branch.py test2
"""

import argparse
import os

parser = argparse.ArgumentParser(description="Set Symfem branch")
parser.add_argument("branch")
branch = parser.parse_args().branch

print(f"Setting Symfem branch to \"{branch}\"")

for file in os.listdir("workflows"):
    skip = False
    content = ""
    with open(os.path.join("workflows", file)) as f:
        for line in f:
            if skip:
                assert "ref:" in line
                skip = False
            else:
                content += line
            if "repository: mscroggs/symfem" in line:
                content += line.split("repository")[0]
                content += f"ref: {branch}\n"
                skip = True
    with open(os.path.join("workflows", file), "w") as f:
        f.write(content)
