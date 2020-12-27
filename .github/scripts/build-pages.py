import re
import os
import argparse
from symfem import create_element

dir_path = os.path.dirname(os.path.realpath(__file__))
element_path = os.path.join(dir_path, "../../elements")
template_path = os.path.join(dir_path, "../../templates")
files_path = os.path.join(dir_path, "../../files")
pages_path = os.path.join(dir_path, "../../pages")

parser = argparse.ArgumentParser(description="Build defelement.com")
parser.add_argument(
    'destination', metavar='destination', nargs="?",
    default=os.path.join(dir_path, "../../_html"),
    help="Destination of HTML files.")

args = parser.parse_args()
html_path = args.destination
htmlelement_path = os.path.join(html_path, "elements")


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


def make_html_page(content):
    out = ""
    with open(os.path.join(template_path, "intro.html")) as f:
        out += f.read()
    out += content
    with open(os.path.join(template_path, "outro.html")) as f:
        out += f.read()
    return out


def markup(content):
    out = ""
    popen = False
    for line in content.split("\n"):
        if line.startswith("#"):
            if popen:
                out += "</p>\n"
                popen = False
            i = 0
            while line.startswith("#"):
                line = line[1:]
                i += 1
            out += f"<h{i}>{line.strip()}</h{i}>\n"
        elif line == "":
            if popen:
                out += "</p>\n"
                popen = False
        else:
            if not popen:
                out += "<p>"
                popen = True
            out += line + " "

    out = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r"<a href='\2'>\1</a>", out)

    return out


if os.path.isdir(html_path):
    os.system(f"rm -rf {html_path}")
os.mkdir(html_path)
os.mkdir(htmlelement_path)

os.system(f"cp -r {files_path}/* {html_path}")

with open(os.path.join(html_path, "CNAME"), "w") as f:
    f.write("defelement.com")

for file in os.listdir(pages_path):
    if file.endswith(".md"):
        fname = file[:-3]
        with open(os.path.join(pages_path, file)) as f:
            content = markup(f.read())

        with open(os.path.join(html_path, f"{fname}.html"), "w") as f:
            f.write(make_html_page(content))

def to_2d(c):
    if len(c) == 1:
        return (10 + c[0] * 100, 110)
    if len(c) == 2:
        return (10 + c[0] * 100, 110 - 100 * c[1])
    return (10 + c[0] * 100, 110 - 100 * c[1])


elementlist = []
for file in os.listdir(element_path):
    if file.endswith(".def") and not file.startswith("."):
        with open(os.path.join(element_path, file)) as f:
            data = parse_file(f.read())
        fname = file[:-4]

        content = f"<h1>{data['name']}</h1>"

        for cell, element_type in data["symfem"].items():
            element = create_element(cell, element_type, 1)

            content += f"<h2>{cell}</h2>\n"
            content += "<svg width='120' height='120'>\n"
            for edge in element.reference.edges:
                p0 = to_2d(element.reference.vertices[edge[0]])
                p1 = to_2d(element.reference.vertices[edge[1]])
                content += f"<line x1='{p0[0]}' y1='{p0[1]}' x2='{p1[0]}' y2='{p1[1]}' stroke-width='4px' stroke-linecap='round' stroke='#AAAAAA' />"
            content += "</svg>\n"

        elementlist.append((data['name'], f"{fname}.html"))

        with open(os.path.join(htmlelement_path, f"{fname}.html"), "w") as f:
            f.write(make_html_page(content))

elementlist.sort(key=lambda x: x[0])

content = "<h1>Index of elements</h1>\n<ul>"
content += "".join([f"<li><a href='/elements/{j}'>{i}</a></li>" for i, j in elementlist])
content += "</ul>"

with open(os.path.join(htmlelement_path, "index.html"), "w") as f:
    f.write(make_html_page(content))
