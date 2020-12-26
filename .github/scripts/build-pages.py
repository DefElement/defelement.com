import os
import argparse
from symfem import create_element


def set(data, keys, value):
    print(keys, value)
    if len(keys) == 1:
        data[keys[0]] = value
        return

    if keys[0] not in data:
        data[keys[0]] = {}

    return set(data[keys[0]], keys[1:], value)


def parse_file(txt):
    data = {}
    keys = tuple()
    for line in txt.split("\n"):
        if line.strip() != "":
            level = 0
            while line.startswith(" " * 2 * (level + 1)):
                level += 1
            keys = keys[:level]
            if ":" in line:
                keys += (line.split(":")[0].strip(), )
                if not line.endswith(":"):
                    set(data, keys, line.split(":")[1].strip())
            else:
                keys += (None, )
                set(data, keys, line.strip())
    return data


dir_path = os.path.dirname(os.path.realpath(__file__))
def_path = os.path.join(dir_path, "../../def")

parser = argparse.ArgumentParser(description="Build defelement.com")
parser.add_argument(
    'destination', metavar='destination', nargs="?",
    default=os.path.join(dir_path, "../../_html"),
    help="Destination of HTML files.")

args = parser.parse_args()
html_path = args.destination

if not os.path.isdir(html_path):
    os.mkdir(html_path)

with open(os.path.join(html_path, "index.html"), "w") as f:
    f.write("<h1>TESTINg</h1>")

exit()

for file in os.listdir(element_path):
    if file.endswith(".def") and not file.startswith("."):
        with open(os.path.join(element_path, file)) as f:
            data = parse_file(f.read())

        with open(os.path.join(def_path, f"{data['name']}.md"), "w") as f:
            f.write("---\n")
            f.write(f"title: {data['name']}\n")
            f.write("---\n")

            for cell, element_type in data["symfem"].items():
                element = create_element(cell, element_type, 1)
                print(element)
