import os
import argparse
import yaml
from symfem import create_element
from markup import markup, insert_dates
from elements import markup_element
from citations import markup_citation, make_bibtex
from polyset import make_poly_set, make_extra_info

dir_path = os.path.dirname(os.path.realpath(__file__))
element_path = os.path.join(dir_path, "../elements")
template_path = os.path.join(dir_path, "../templates")
files_path = os.path.join(dir_path, "../files")
pages_path = os.path.join(dir_path, "../pages")
data_path = os.path.join(dir_path, "../data")

parser = argparse.ArgumentParser(description="Build defelement.com")
parser.add_argument(
    'destination', metavar='destination', nargs="?",
    default=os.path.join(dir_path, "../_html"),
    help="Destination of HTML files.")
parser.add_argument('--test', action="store_true",
                    help="Builds a version of the website with fewer elements.")

args = parser.parse_args()
html_path = args.destination
htmlelement_path = os.path.join(html_path, "elements")
htmlindices_path = os.path.join(html_path, "lists")

test_mode = args.test


def make_html_page(content):
    out = ""
    with open(os.path.join(template_path, "intro.html")) as f:
        out += insert_dates(f.read())
    out += content
    with open(os.path.join(template_path, "outro.html")) as f:
        out += insert_dates(f.read())
    return out


if os.path.isdir(html_path):
    os.system(f"rm -rf {html_path}")
os.mkdir(html_path)
os.mkdir(htmlelement_path)
os.mkdir(htmlindices_path)
os.mkdir(os.path.join(htmlelement_path, "bibtex"))

os.system(f"cp -r {files_path}/* {html_path}")

with open(os.path.join(html_path, "CNAME"), "w") as f:
    f.write("defelement.com")

categories = {}
with open(os.path.join(data_path, "categories")) as f:
    for line in f:
        a, b = line.split(":", 1)
        categories[a.strip()] = b.strip()

category_pages = {i: [] for i in categories.keys()}

for file in os.listdir(pages_path):
    if file.endswith(".md"):
        fname = file[:-3]
        with open(os.path.join(pages_path, file)) as f:
            content = markup(f.read())

        with open(os.path.join(html_path, f"{fname}.html"), "w") as f:
            f.write(make_html_page(content))

elementlist = []
refels = {}


def dofs_on_entity(entity, dofs):
    global elementlist
    if "integral moment" in dofs:
        mom_type, space_info = dofs.split(" with ")
        space, order = space_info.split("(")[1].split(")")[0].split(",")
        space = space.strip()
        order = order.strip()
        space_link = "*ERROR*"
        for i, j, k in elementlist:
            if k == space:
                space_link = f"<a href='/elements/{j}'>{i}</a>"
        assert space_link != "*ERROR*"
        return f"{mom_type} with an order \\({order}\\) {space_link} space"
    return dofs


for file in os.listdir(element_path):
    if file.endswith(".def") and not file.startswith("."):
        with open(os.path.join(element_path, file)) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        fname = file[:-4]
        elementlist.append((data['html-name'], f"{fname}.html", fname))

for file in os.listdir(element_path):
    if file.endswith(".def") and not file.startswith("."):
        with open(os.path.join(element_path, file)) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        if test_mode and "test" not in data:
            continue

        print(data["name"])
        fname = file[:-4]
        content = f"<h1>{data['html-name'][0].upper()}{data['html-name'][1:]}</h1>"
        element_data = []

        # Alternative names
        if "alt-names" in data:
            element_data.append(("Alternative names", ", ".join(data["alt-names"])))

        # Orders
        if "min-order" in data:
            min_o = data["min-order"]
        else:
            min_o = 0
        if 'max-order' in data:
            element_data.append(("Orders",
                                 f"\\({min_o}\\leqslant k\\leqslant {data['max-order']}\\)"))
        else:
            element_data.append(("Orders", f"\\({min_o}\\leqslant k\\)"))

        # Reference elements
        for e in data["reference elements"]:
            if e not in refels:
                refels[e] = []
            refels[e].append((data["html-name"], f"{fname}.html"))
        element_data.append(
            ("Reference elements",
             ", ".join([f"<a href='/lists/references/{e}.html'>{e}</a>"
                        for e in data["reference elements"]])))

        # Polynomial set
        if "polynomial set" in data:
            psets = {}
            for i, j in data["polynomial set"].items():
                if j not in psets:
                    psets[j] = []
                psets[j].append(i)
            set_data = "<ul>\n"
            for i, j in psets.items():
                set_data += f"<li>\\({make_poly_set(i)}\\) ({', '.join(j)})</li>\n"
            set_data += "</ul>\n"
            extra = make_extra_info(" & ".join(psets.keys()))
            if len(extra) > 0:
                set_data += "<a id='show_pset_link' href='javascript:show_psets()'>"
                set_data += "Show polynomial set definitions</a>"
                set_data += "<a id='hide_pset_link' href='javascript:hide_psets()'"
                set_data += " style='display:none'>"
                set_data += "Hide polynomial set definitions</a>"
                set_data += "<div id='psets' style='display:none'>"
                set_data += extra
                set_data += "</div>"
                set_data += "<script type='text/javascript'>\n"
                set_data += "function show_psets(){\n"
                set_data += "   document.getElementById('show_pset_link').style.display = 'none'\n"
                set_data += "   document.getElementById('hide_pset_link').style.display = 'block'\n"
                set_data += "   document.getElementById('psets').style.display = 'block'\n"
                set_data += "}\n"
                set_data += "function hide_psets(){\n"
                set_data += "   document.getElementById('show_pset_link').style.display = 'block'\n"
                set_data += "   document.getElementById('hide_pset_link').style.display = 'none'\n"
                set_data += "   document.getElementById('psets').style.display = 'none'\n"
                set_data += "}\n"
                set_data += "</script>"
            element_data.append(("Polynomial set", set_data))

        # DOFs
        if "dofs" in data:
            dof_data = []
            for i, j in [
                ("On each vertex", "vertices"),
                ("On each edge", "edges"),
                ("On each face", "faces"),
                ("On each volume", "volumes"),
                ("On each ridge", "ridges"),
                ("On each peak", "peaks"),
                ("On each facet", "facets"),
                ("On the interior of the reference element", "cell"),
            ]:
                if j in data["dofs"]:
                    dof_data.append(f"<li>{i}: {dofs_on_entity(j, data['dofs'][j])}</li>")
            if len(dof_data) > 0:
                element_data.append(("DOFs", "<ul>\n" + "\n".join(dof_data) + "</ul>"))

        # Categories
        if "categories" in data:
            for c in data["categories"]:
                category_pages[c].append((data["html-name"], f"{fname}.html"))
            element_data.append(
                ("Categories",
                 ", ".join([f"<a href='/lists/categories/{c}.html'>{categories[c]}</a>"
                            for c in data["categories"]])))

        # Write element data
        content += "<table class='element-info'>"
        for i, j in element_data:
            content += f"<tr><td>{i}</td><td>{j}</td></tr>"
        content += "</table>"

        # Write examples using symfem
        element_names = []
        element_examples = []

        if "examples" in data:
            for e in data["examples"]:
                cell = e.split(",")[0]
                order = int(e.split(",")[1])
                element_type = data["symfem"][cell]

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
            for i, r in enumerate(data["references"]):
                content += f"<li>{markup_citation(r)}"
                content += f" [<a href='/elements/bibtex/{fname}-{i}.bib'>BibTeX</a>]</li>\n"
                with open(os.path.join(htmlelement_path, f"bibtex/{fname}-{i}.bib"), "w") as f:
                    f.write(make_bibtex(f"{fname}-{i}", r))
            content += "</ul>"

        # Write file
        with open(os.path.join(htmlelement_path, f"{fname}.html"), "w") as f:
            f.write(make_html_page(content))

# Index page
elementlist.sort(key=lambda x: x[0])

content = "<h1>Index of elements</h1>\n<ul>"
content += "".join([f"<li><a href='/elements/{j}'>{i}</a></li>" for i, j, k in elementlist])
content += "</ul>"

with open(os.path.join(htmlelement_path, "index.html"), "w") as f:
    f.write(make_html_page(content))
with open(os.path.join(htmlindices_path, "index.html"), "w") as f:
    f.write(make_html_page(content))


# Category index
os.mkdir(os.path.join(htmlindices_path, "categories"))
content = f"<h1>Categories</h1>\n"
for c in categories:
    category_pages[c].sort(key=lambda x: x[0])

    content += f"<h2><a name='{c}'></a>{categories[c]}</h2>\n<ul>"
    content += "".join([f"<li><a href='/elements/{j}'>{i}</a></li>" for i, j in category_pages[c]])
    content += "</ul>"

    sub_content = f"<h1>{categories[c]}</h1>\n<ul>"
    sub_content += "".join([f"<li><a href='/elements/{j}'>{i}</a></li>"
                            for i, j in category_pages[c]])
    sub_content += "</ul>"

    with open(os.path.join(htmlindices_path, f"categories/{c}.html"), "w") as f:
        f.write(make_html_page(sub_content))

with open(os.path.join(htmlindices_path, "categories/index.html"), "w") as f:
    f.write(make_html_page(content))

# Reference elements index
os.mkdir(os.path.join(htmlindices_path, "references"))
content = f"<h1>Reference elements</h1>\n"
for c in refels:
    refels[c].sort(key=lambda x: x[0])

    content += f"<h2><a name='{c}'></a>{c[0].upper()}{c[1:]}</h2>\n<ul>"
    content += "".join([f"<li><a href='/elements/{j}'>{i}</a></li>" for i, j in refels[c]])
    content += "</ul>"

    sub_content = "<h1>Finite elements on a"
    if c[0] in "aeiou":
        sub_content += "n"
    sub_content += f" {c}</h1>\n<ul>"
    sub_content += "".join([f"<li><a href='/elements/{j}'>{i}</a></li>" for i, j in refels[c]])
    sub_content += "</ul>"

    with open(os.path.join(htmlindices_path, f"references/{c}.html"), "w") as f:
        f.write(make_html_page(sub_content))

with open(os.path.join(htmlindices_path, "references/index.html"), "w") as f:
    f.write(make_html_page(content))

# List of lists
content = "<h1>Lists of elements</h1>\n<ul>\n"
content += "<li><a href='/lists/categories'>Finite elements by category</a></li>\n"
content += "<li><a href='/lists/references'>Finite elements by reference element</a></li>\n"
content += "</ul>"
with open(os.path.join(htmlindices_path, "index.html"), "w") as f:
    f.write(make_html_page(content))
