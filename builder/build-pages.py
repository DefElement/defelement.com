import os
import argparse
import yaml
from symfem import create_element
from markup import markup, markup_element, markup_citation

dir_path = os.path.dirname(os.path.realpath(__file__))
element_path = os.path.join(dir_path, "../elements")
template_path = os.path.join(dir_path, "../templates")
files_path = os.path.join(dir_path, "../files")
pages_path = os.path.join(dir_path, "../pages")

parser = argparse.ArgumentParser(description="Build defelement.com")
parser.add_argument(
    'destination', metavar='destination', nargs="?",
    default=os.path.join(dir_path, "../_html"),
    help="Destination of HTML files.")

args = parser.parse_args()
html_path = args.destination
htmlelement_path = os.path.join(html_path, "elements")


def make_html_page(content):
    out = ""
    with open(os.path.join(template_path, "intro.html")) as f:
        out += f.read()
    out += content
    with open(os.path.join(template_path, "outro.html")) as f:
        out += f.read()
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

elementlist = []
for file in os.listdir(element_path):
    if file.endswith(".def") and not file.startswith("."):
        with open(os.path.join(element_path, file)) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        fname = file[:-4]

        content = f"<h1>{data['name']}</h1>"

        # Write examples using symfem
        element_names = []
        element_examples= []

        if "symfem" in data:
            for cell, element_type in data["symfem"].items():
                for order in [1, 2]:
                    element = create_element(cell, element_type, order)

                    eg = markup_element(element)

                    if eg != "":
                        element_names.append(f"{cell}<br />order {order}")
                        element_examples.append(eg)

        if len(element_names) > 0:
            content += f"<h2>Examples</h2>\n"
            for i, e in enumerate(element_names):
                cl = "eglink"
                if i == 0:
                    cl += " current"
                content += f"<a class='{cl}' href='javascript:showeg({i})' id='eg{i}'>{e}</a>"
            for i, e in enumerate(element_examples):
                cl = "egdetail"
                if i == 0:
                    cl += " current"
                content += f"<div class='{cl}' id='egd{i}'>{e}</div>"

            content += "<script type='text/javascript'>\n"
            content += "function showeg(i){\n"
            content += f"    for(var j=0;j<{len(element_names)};j++){{\n"
            content += "        if(i==j){\n"
            content += "            document.getElementById('eg'+j).className='eglink current'\n"
            content += "            document.getElementById('egd'+j).className='egdetail current'\n"
            content += "        } else {\n"
            content += "            document.getElementById('eg'+j).className='eglink'\n"
            content += "            document.getElementById('egd'+j).className='egdetail'\n"
            content += "        }\n"
            content += "    }\n"
            content += "}\n"
            content += "</script>"

        # Write references section
        if "references" in data:
            content += "<h2>References</h2>\n"
            content += "<ul class='citations'>\n"
            for r in data["references"]:
                content += f"<li>{markup_citation(r)}</li>\n"
            content += "</ul>"

        # Write file
        elementlist.append((data['name'], f"{fname}.html"))

        with open(os.path.join(htmlelement_path, f"{fname}.html"), "w") as f:
            f.write(make_html_page(content))

elementlist.sort(key=lambda x: x[0])

content = "<h1>Index of elements</h1>\n<ul>"
content += "".join([f"<li><a href='/elements/{j}'>{i}</a></li>" for i, j in elementlist])
content += "</ul>"

with open(os.path.join(htmlelement_path, "index.html"), "w") as f:
    f.write(make_html_page(content))
