import os
import argparse
import yaml
from symfem import create_element
from markup import markup, insert_dates, insert_links, python_highlight
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
htmlfamilies_path = os.path.join(html_path, "families")

test_mode = args.test


def make_html_page(content, pagetitle=None):
    out = ""
    with open(os.path.join(template_path, "intro.html")) as f:
        out += insert_dates(f.read())
    if pagetitle is None:
        out = out.replace("{{: pagetitle}}", "")
    else:
        out = out.replace("{{: pagetitle}}", f": {pagetitle}")
    out += content
    with open(os.path.join(template_path, "outro.html")) as f:
        out += insert_dates(f.read())
    return out


if os.path.isdir(html_path):
    os.system(f"rm -rf {html_path}")
os.mkdir(html_path)
os.mkdir(htmlelement_path)
os.mkdir(htmlindices_path)
os.mkdir(htmlfamilies_path)
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
ec_families = {}


def dofs_on_entity(entity, dofs):
    global elementlist
    if not isinstance(dofs, str):
        doflist = [dofs_on_entity(entity, d) for d in dofs]
        return ", ".join(doflist[:-1]) + ", and " + doflist[-1]
    if "integral moment" in dofs:
        mom_type, space_info = dofs.split(" with ")
        space, order = space_info.split("(")[1].split(")")[0].split(",")
        space = space.strip()
        order = order.strip()
        space_link = "*ERROR*"
        if space == "arnold-winther-extras":
            out = f"{mom_type} with \\(\\frac{{\\partial}}{{\\partial(x, y)}}x^2y^2(1-x-y)^2f\\)"
            out += f" for each order \\({order}\\) polynomial \\(f\\) in an order \\({order}\\)"
            out += " <a href='/elements/lagrange.html'>Lagrange</a> space"
            return out
        if space == "bernstein-polynomials":
            return f"{mom_type} with order \\({order}\\) Bernstein polynomials"
        for i, j, k, _, _ in elementlist:
            if k == space:
                space_link = f"<a href='/elements/{j}'>{i}</a>"
                break
        assert space_link != "*ERROR*"
        return f"{mom_type} with an order \\({order}\\) {space_link} space"
    return dofs


def make_dof_descs(data, post=""):
    dof_data = []
    for i in ["interval", "triangle", "tetrahedron", "quadrilateral", "hexahedron"]:
        if i in data:
            dof_data.append(make_dof_descs(data[i], f" ({i})"))
    if len(dof_data) != 0:
        return "<br />\n<br />\n".join(dof_data)

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
        if j in data:
            dof_data.append(f"{i}{post}: {dofs_on_entity(j, data[j])}")
    return "<br />\n".join(dof_data)


def make_order_data(min_o, max_o):
    if isinstance(min_o, dict):
        orders = []
        for i, min_i in min_o.items():
            if isinstance(max_o, dict) and i in max_o:
                orders.append(i + ": " + make_order_data(min_i, max_o[i]))
            else:
                orders.append(i + ": " + make_order_data(min_i, max_o))
        return "<br />\n".join(orders)
    if max_o is None:
        return f"\\({min_o}\\leqslant k\\)"
    if max_o == min_o:
        return f"\\(k={min_o}\\)"
    return f"\\({min_o}\\leqslant k\\leqslant {max_o}\\)"


for file in os.listdir(element_path):
    if file.endswith(".def") and not file.startswith("."):
        with open(os.path.join(element_path, file)) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        fname = file[:-4]
        if "categories" in data:
            cats = data["categories"]
        else:
            cats = []
        elementlist.append((data['html-name'], f"{fname}.html", fname,
                            data["reference elements"], cats))

        if "alt-names" in data:
            for i in data["alt-names"]:
                if i[0] == "(" and i[-1] == ")":
                    continue
                if " (" in i:
                    elementlist.append((i.split(" (")[0], f"{fname}.html", fname,
                                        [j.strip() for j in i.split(" (")[1].split(",")],
                                        cats))
                else:
                    elementlist.append((i, f"{fname}.html", fname,
                                        data["reference elements"], cats))

for file in os.listdir(element_path):
    if file.endswith(".def") and not file.startswith("."):
        with open(os.path.join(element_path, file)) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        print(data["name"])
        fname = file[:-4]
        content = f"<h1>{data['html-name'][0].upper()}{data['html-name'][1:]}</h1>"
        element_data = []

        # Link to ciarlet.htmlk
        content += "<p><small><a href='/ciarlet.html'>"
        content += "Click here to read what the information on this page means."
        content += "</a></small></p>"

        # Alternative names
        alt_names = []
        if "alt-names" in data:
            alt_names = [i[1:-1] if i[0] == "(" and i[-1] == ")" else i
                         for i in data["alt-names"]]
        if "exterior-calculus" in data:
            ec = data["exterior-calculus"]
            if not isinstance(ec, (list, tuple)):
                ec = [ec]
            for e in ec:
                i, j, k = e.split(",")
                if i not in ec_families:
                    ec_families[i] = {}
                if k not in ec_families[i]:
                    ec_families[i][k] = {}
                ec_families[i][k][j] = (data["html-name"], f"{fname}.html")
                name = f"<a href='/families/{i}.html'>\\(\\mathcal{{{i[0]}}}"
                if len(i) > 1:
                    name += f"^{i[1]}"
                name += f"_k\\Lambda^{{{j}}}("
                if k == "simplex":
                    name += "\\Delta"
                else:
                    assert k == "tp"
                    name += "\\square"
                name += "_d)"
                name += "\\)</a>"
                alt_names.append(name)
        if len(alt_names) > 0:
            element_data.append(("Alternative names", ", ".join(alt_names)))

        # Short names
        if "short-names" in data:
            element_data.append(("Abbreviated names", ", ".join(data["short-names"])))

        # Orders
        element_data.append(("Orders", make_order_data(
            data["min-order"] if "min-order" in data else 0,
            data["max-order"] if "max-order" in data else None)))

        # Reference elements
        for e in data["reference elements"]:
            if e not in refels:
                refels[e] = []
            refels[e].append((data["html-name"], f"{fname}.html"))
            if "alt-names" in data:
                for i in data["alt-names"]:
                    if i[0] == "(" and i[-1] == ")":
                        continue

                    refels[e].append((i.split(" (")[0], f"{fname}.html"))
        element_data.append(
            ("Reference elements",
             ", ".join([f"<a href='/lists/references/{e}.html'>{e}</a>"
                        for e in data["reference elements"]])))

        # Mixed elements
        if "mixed" in data:
            subelements = []
            for e in data["mixed"]:
                e_type, order = e.split("(")
                order = order.split(")")[0]
                for i, j, k, _, _ in elementlist:
                    if k == e_type:
                        space_link = f"<a href='/elements/{j}'>{i}</a>"
                        break
                assert space_link != "*ERROR*"
                subelements.append(f"<li>order \\({order}\\) {space_link} space</li>")
            element_data.append(
                ("Definition",
                 "This is a mixed element containing these subelements:"
                 "<ul>" + "\n".join(subelements) + "</ul>"))

        # Polynomial set
        if "polynomial set" in data:
            psets = {}
            for i, j in data["polynomial set"].items():
                if j not in psets:
                    psets[j] = []
                psets[j].append(i)
            if (
                "reference elements" in data and len(psets) == 1
                and len(list(psets.values())[0]) == len(data["reference elements"])
            ):
                set_data = f"\\({make_poly_set(list(psets.keys())[0])}\\)<br />"
            else:
                set_data = ""
                for i, j in psets.items():
                    set_data += f"\\({make_poly_set(i)}\\) ({', '.join(j)})<br />\n"
            extra = make_extra_info(" && ".join(psets.keys()))
            if len(extra) > 0:
                set_data += "<a id='show_pset_link' href='javascript:show_psets()'"
                set_data += " style='display:block'>"
                set_data += "&darr; Show polynomial set definitions &darr;</a>"
                set_data += "<a id='hide_pset_link' href='javascript:hide_psets()'"
                set_data += " style='display:none'>"
                set_data += "&uarr; Hide polynomial set definitions &uarr;</a>"
                set_data += "<div id='psets' style='display:none'>"
                set_data += extra
                set_data += "</div>"
                set_data += "<script type='text/javascript'>\n"
                set_data += "function show_psets(){\n"
                set_data += "  document.getElementById('show_pset_link').style.display = 'none'\n"
                set_data += "  document.getElementById('hide_pset_link').style.display = 'block'\n"
                set_data += "  document.getElementById('psets').style.display = 'block'\n"
                set_data += "}\n"
                set_data += "function hide_psets(){\n"
                set_data += "  document.getElementById('show_pset_link').style.display = 'block'\n"
                set_data += "  document.getElementById('hide_pset_link').style.display = 'none'\n"
                set_data += "  document.getElementById('psets').style.display = 'none'\n"
                set_data += "}\n"
                set_data += "</script>"
            element_data.append(("Polynomial set", set_data))

        # DOFs
        if "dofs" in data:
            dof_data = make_dof_descs(data["dofs"])
            if len(dof_data) > 0:
                element_data.append(("DOFs", dof_data))

        # Number of DOFs
        if "ndofs" in data or "ndofs-oeis" in data:
            dof_data = {}
            if "ndofs" in data:
                for e, formula in data["ndofs"].items():
                    if e not in dof_data:
                        dof_data[e] = {}
                    dof_data[e]["formula"] = formula
            if "ndofs-oeis" in data:
                for e, oeis in data["ndofs-oeis"].items():
                    if e not in dof_data:
                        dof_data[e] = {}
                    dof_data[e]["oeis"] = oeis

            if len(dof_data) > 0:
                dof_text = []
                for i, j in dof_data.items():
                    if "formula" in j and "oeis" in j:
                        dof_text.append(
                            f"{i}: \\({j['formula']}\\)"
                            f" (<a href='http://oeis.org/{j['oeis']}'>{j['oeis']}</a>)")
                    elif "formula" in j:
                        dof_text.append(f"{i}: \\({j['formula']}\\)")
                    elif "oeis" in j:
                        dof_text.append(f"<a href='http://oeis.org/{j['oeis']}'>{j['oeis']}</a>")
                element_data.append(("Number of DOFs", "<br />\n".join(dof_text)))

        # Notes
        if "notes" in data:
            element_data.append(
                ("Notes",
                 "<br />\n".join([insert_links(i) for i in data["notes"]])))

        # Symfem string
        if "symfem" in data:
            symfem_info = f"<code>\"{data['symfem']}\"</code>"
            symfem_info += "<br />"

            symfem_info += "<a id='show_symfem_link' href='javascript:show_symfem_eg()'"
            symfem_info += " style='display:block'>"
            symfem_info += "&darr; Show Symfem examples &darr;</a>"
            symfem_info += "<a id='hide_symfem_link' href='javascript:hide_symfem_eg()'"
            symfem_info += " style='display:none'>"
            symfem_info += "&uarr; Hide Symfem examples &uarr;</a>"
            symfem_info += "<div id='symfem_eg' style='display:none'>"
            symfem_info += "Before trying this example, you must install "
            symfem_info += "<a href='https://github.com/mscroggs/symfem'>Symfem</a>:"
            symfem_info += "<p class='pcode'>pip3 install symfem</p>"
            symfem_info += "This element can then be created with the following lines of Python:"
            symfem_example = "import symfem"
            for ref in data["reference elements"]:
                if "min-order" in data:
                    if isinstance(data["min-order"], dict):
                        min_o = data["min-order"][ref]
                    else:
                        min_o = data["min-order"]
                else:
                    min_o = 0
                max_o = min_o + 2
                if "max-order" in data:
                    if isinstance(data["max-order"], dict):
                        max_o = min(data["max-order"][ref], max_o)
                    else:
                        max_o = min(data["max-order"], max_o)
                print(min_o, max_o)
                for ord in range(min_o, max_o + 1):
                    symfem_example += "\n\n"
                    symfem_example += f"# Create {data['name']} order {ord} on a {ref}\n"
                    symfem_example += f"element = symfem.create_element(\"{ref}\","
                    if "variant=" in data["symfem"]:
                        e_name, variant = data["symfem"].split(" variant=")
                        symfem_example += f" \"{e_name}\", {ord}, \"{variant}\")"
                    else:
                        symfem_example += f" \"{data['symfem']}\", {ord})"
            symfem_info += "<p class='pcode'>" + python_highlight(symfem_example) + "</p>"
            symfem_info += "</div>"
            symfem_info += "<script type='text/javascript'>\n"
            symfem_info += "function show_symfem_eg(){\n"
            symfem_info += "  document.getElementById('show_symfem_link').style.display = 'none'\n"
            symfem_info += "  document.getElementById('hide_symfem_link').style.display = 'block'\n"
            symfem_info += "  document.getElementById('symfem_eg').style.display = 'block'\n"
            symfem_info += "}\n"
            symfem_info += "function hide_symfem_eg(){\n"
            symfem_info += "  document.getElementById('show_symfem_link').style.display = 'block'\n"
            symfem_info += "  document.getElementById('hide_symfem_link').style.display = 'none'\n"
            symfem_info += "  document.getElementById('symfem_eg').style.display = 'none'\n"
            symfem_info += "}\n"
            symfem_info += "</script>"

            element_data.append(("Symfem string", symfem_info))

        # Categories
        if "categories" in data:
            for c in data["categories"]:
                category_pages[c].append((data["html-name"], f"{fname}.html"))
                if "alt-names" in data:
                    for i in data["alt-names"]:
                        if i[0] == "(" and i[-1] == ")":
                            continue
                        category_pages[c].append((i.split(" (")[0], f"{fname}.html"))
            element_data.append(
                ("Categories",
                 ", ".join([f"<a href='/lists/categories/{c}.html'>{categories[c]}</a>"
                            for c in data["categories"]])))

        # Write element data
        content += "<table class='element-info'>"
        for i, j in element_data:
            content += f"<tr><td>{i.replace(' ', '&nbsp;')}</td><td>{j}</td></tr>"
        content += "</table>"

        # Write examples using symfem
        element_names = []
        element_examples = []

        if (not test_mode or "test" in data) and "examples" in data:
            for e in data["examples"]:
                cell = e.split(",")[0]
                order = int(e.split(",")[1])
                if "variant=" in data["symfem"]:
                    element_type, variant = data["symfem"].split(" variant=")
                    element = create_element(cell, element_type, order, variant)
                else:
                    element_type = data["symfem"]
                    element = create_element(cell, element_type, order)

                eg = markup_element(element)

                if eg != "":
                    element_names.append(f"{cell}<br />order {order}")
                    element_examples.append(eg)

        if len(element_names) > 0:
            content += "<h2>Examples</h2>\n"
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
            f.write(make_html_page(content, data["html-name"]))

# Index page
elementlist.sort(key=lambda x: x[0].lower())

content = "<h1>Index of elements</h1>\n"
# Generate filtering Javascript
content += "<script type='text/javascript'>\n"
content += "function do_filter_refall(){\n"
content += "    if(document.getElementById('check-ref-all').checked){\n"
for r in refels:
    content += f"        document.getElementById('check-ref-{r}').checked = false\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter_catall(){\n"
content += "    if(document.getElementById('check-cat-all').checked){\n"
for c in categories:
    content += f"        document.getElementById('check-cat-{c}').checked = false\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter_cat(){\n"
content += "    if(document.getElementById('check-cat-all').checked){\n"
content += "        if("
content += " || ".join([f"document.getElementById('check-cat-{c}').checked" for c in categories])
content += "){"
content += "            document.getElementById('check-cat-all').checked = false\n"
content += "        }\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter_ref(){\n"
content += "    if(document.getElementById('check-ref-all').checked){\n"
content += "        if("
content += " || ".join([f"document.getElementById('check-ref-{r}').checked" for r in refels])
content += "){"
content += "            document.getElementById('check-ref-all').checked = false\n"
content += "        }\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter(){\n"
content += "    var els = document.getElementsByClassName('element-on-list')\n"
content += "    for(var i=0; i < els.length; i++){\n"
content += "        var ref_show = false\n"
content += "        if(document.getElementById('check-ref-all').checked){\n"
content += "            ref_show = true\n"
content += "        } else {\n"
for r in refels:

    content += f"            if(document.getElementById('check-ref-{r}').checked"
    content += f" && els[i].id.indexOf('ref-{r}') != -1){{ref_show = true}}\n"
content += "        }\n"
content += "        var cat_show = false\n"
content += "        if(document.getElementById('check-cat-all').checked){\n"
content += "            cat_show = true\n"
content += "        } else {\n"
for c in categories:

    content += f"            if(document.getElementById('check-cat-{c}').checked"
    content += f" && els[i].id.indexOf('cat-{c}') != -1){{cat_show = true}}\n"
content += "        }\n"
content += "        if(cat_show && ref_show){\n"
content += "            els[i].style.display='block'\n"
content += "        } else {\n"
content += "            els[i].style.display='none'\n"
content += "        }\n"
content += "    }\n"
content += "}\n"
content += "function show_filtering(){\n"
content += "    document.getElementById('show-flink').style.display='none'\n"
content += "    document.getElementById('hide-flink').style.display='block'\n"
content += "    document.getElementById('the-filters').style.display='block'\n"
content += "}\n"
content += "function hide_filtering(){\n"
content += "    document.getElementById('show-flink').style.display='block'\n"
content += "    document.getElementById('hide-flink').style.display='none'\n"
content += "    document.getElementById('the-filters').style.display='none'\n"
content += "}\n"
content += "</script>"
content += "<a href='javascript:show_filtering()' id='show-flink' style='display:block'"
content += ">&darr; Show filters &darr;</a>\n"
content += "<a href='javascript:hide_filtering()' id='hide-flink' style='display:none'"
content += ">&uarr; Hide filters &uarr;</a>\n"
content += "<table id='the-filters' class='filters' style='display:none'>"
content += "<tr><td>Reference&nbsp;elements</td><td>"
content += "<label><input type='checkbox' checked id='check-ref-all' onchange='do_filter_refall()'"
content += ">&nbsp;show all</label> "
for r in refels:
    content += f"<label><input type='checkbox' id='check-ref-{r}' onchange='do_filter_ref()'"
    content += f">&nbsp;{r}</label> "
content += "</td></tr>"
content += "<tr><td>Categories</td><td>"
content += "<label><input type='checkbox' checked id='check-cat-all'onchange='do_filter_catall()'"
content += ">&nbsp;show all</label> "
for c in categories:
    content += f"<label><input type='checkbox' id='check-cat-{c}'onchange='do_filter_cat()'"
    content += f">&nbsp;{categories[c]}</label> "
content += "</td></tr>"
content += "</table>\n"
# Write element list
content += "<ul>"
for i, j, k, refs, cats in elementlist:
    id = " ".join([f"ref-{r}" for r in refs] + [f"cat-{c}" for c in cats])
    content += f"<li class='element-on-list' id='{id}'><a href='/elements/{j}'>{i}</a></li>"
content += "</ul>"

with open(os.path.join(htmlelement_path, "index.html"), "w") as f:
    f.write(make_html_page(content))
with open(os.path.join(htmlindices_path, "index.html"), "w") as f:
    f.write(make_html_page(content))

# Category index
os.mkdir(os.path.join(htmlindices_path, "categories"))
content = "<h1>Categories</h1>\n"
for c in categories:
    category_pages[c].sort(key=lambda x: x[0].lower())

    content += f"<h2><a name='{c}'></a>{categories[c]}</h2>\n<ul>"
    content += "".join([f"<li><a href='/elements/{j}'>{i}</a></l*i>" for i, j in category_pages[c]])
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
content = "<h1>Reference elements</h1>\n"
for c in refels:
    refels[c].sort(key=lambda x: x[0].lower())

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

# Families
content = "<h1>Families</h1>\n"
content += "<ul>\n"
for fname, family in ec_families.items():
    tex_name = f"\\mathcal{{{fname[0]}}}"
    if len(fname) > 1:
        tex_name += f"^{fname[1]}"
    tex_name += "_k\\Lambda"
    sub_content = f"<h1>The \\({tex_name}^r\\) family</h1>"

    sub_content += "<ul>"
    for cell in ["simplex", "tp"]:
        if cell in family:
            for order in ["0", "1", "d-1", "d"]:
                if order in family[cell]:
                    sub_content += f"<li><a href='/elements/{family[cell][order][1]}'"
                    sub_content += " style='text-decoration:none'>"
                    sub_content += f"\\({tex_name}^{{{order}}}("
                    if cell == "simplex":
                        sub_content += "\\Delta"
                    else:
                        sub_content += "\\square"
                    sub_content += f"_d)\\) ({family[cell][order][0]})</a></li>"
    sub_content += "</ul>"

    with open(os.path.join(htmlfamilies_path, f"{fname}.html"), "w") as f:
        f.write(make_html_page(sub_content))

    content += f"<li><a href='/families/{fname}.html'>\\({tex_name}^r\\)</a></li>\n"
content += "</ul>"
with open(os.path.join(htmlfamilies_path, "index.html"), "w") as f:
    f.write(make_html_page(content))

# List of lists
content = "<h1>Lists of elements</h1>\n<ul>\n"
content += "<li><a href='/lists/categories'>Finite elements by category</a></li>\n"
content += "<li><a href='/lists/references'>Finite elements by reference element</a></li>\n"
content += "</ul>"
with open(os.path.join(htmlindices_path, "index.html"), "w") as f:
    f.write(make_html_page(content))
