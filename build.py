import os
import argparse
from symfem import create_element
from builder import settings
from builder.markup import markup, insert_links, python_highlight, cap_first
from builder.examples import markup_example
from builder.citations import markup_citation, make_bibtex
from builder.element import Categoriser
from builder.html import make_html_page
from builder.snippets import parse_example

parser = argparse.ArgumentParser(description="Build defelement.com")
parser.add_argument('destination', metavar='destination', nargs="?",
                    default=None, help="Destination of HTML files.")
parser.add_argument('--test', metavar="test", default=None,
                    help="Builds a version of the website with fewer elements.")
parser.add_argument('--github-token', metavar="github_token", default=None,
                    help="Provide a GitHub token to get update timestamps.")

args = parser.parse_args()
if args.destination is not None:
    settings.html_path = args.destination
    settings.htmlelement_path = os.path.join(settings.html_path, "elements")
    settings.htmlimg_path = os.path.join(settings.html_path, "img")
    settings.htmlindices_path = os.path.join(settings.html_path, "lists")
    settings.htmlfamilies_path = os.path.join(settings.html_path, "families")

if args.github_token is not None:
    settings.github_token = args.github_token

if args.test is None:
    test_elements = None
else:
    test_elements = args.test.split(",")

# Prepare paths
if os.path.isdir(settings.html_path):
    os.system(f"rm -rf {settings.html_path}")
os.mkdir(settings.html_path)
os.mkdir(settings.htmlelement_path)
os.mkdir(settings.htmlindices_path)
os.mkdir(settings.htmlfamilies_path)
os.mkdir(settings.htmlimg_path)
os.mkdir(os.path.join(settings.htmlelement_path, "bibtex"))

os.system(f"cp -r {settings.files_path}/* {settings.html_path}")

with open(os.path.join(settings.html_path, "CNAME"), "w") as f:
    f.write("defelement.com")

# Make pages
for file in os.listdir(settings.pages_path):
    if file.endswith(".md"):
        fname = file[:-3]
        with open(os.path.join(settings.pages_path, file)) as f:
            content = markup(f.read())

        with open(os.path.join(settings.html_path, f"{fname}.html"), "w") as f:
            f.write(make_html_page(content))

# Load categories and reference elements
categoriser = Categoriser()
categoriser.load_categories(os.path.join(settings.data_path, "categories"))
categoriser.load_references(os.path.join(settings.data_path, "references"))

# Load elements from .def files
categoriser.load_folder(settings.element_path)

# Generate element pages
for e in categoriser.elements:
    print(e.name)
    content = f"<h1>{cap_first(e.html_name)}</h1>"
    element_data = []
    implementations = []

    # Link to ciarlet.html
    content += "<p><small><a href='/ciarlet.html'>"
    content += "Click here to read what the information on this page means."
    content += "</a></small></p>"

    # Alternative names
    alt_names = e.alternative_names()
    if len(alt_names) > 0:
        element_data.append(("Alternative names", ", ".join(alt_names)))

    # Short names
    short_names = e.short_names()
    if len(short_names) > 0:
        element_data.append(("Abbreviated names", ", ".join(short_names)))

    # Orders
    element_data.append(("Orders", e.order_range()))

    # Reference elements
    refs = e.reference_elements()
    element_data.append(("Reference elements", ", ".join(refs)))

    # Mixed elements
    if e.is_mixed:
        subelements = e.sub_elements()
        element_data.append(
            ("Definition",
             "This is a mixed element containing these subelements:"
             "<ul>" + "\n".join(subelements) + "</ul>"))

    # Polynomial set
    psets = e.make_polynomial_set_html()
    if len(psets) > 0:
        element_data.append(("Polynomial set", psets))

    # DOFs
    dofs = e.make_dof_descriptions()
    if len(dofs) > 0:
        element_data.append(("DOFs", dofs))

    # Number of DOFs
    ndofs = e.dof_counts()
    if len(ndofs) > 0:
        element_data.append(("Number of DOFs", ndofs))

    # Number of DOFs on subentities
    ndofs = e.entity_dof_counts()
    if len(ndofs) > 0:
        element_data.append(("Number of DOFs<breakable>on subentities", ndofs))

    # Notes
    notes = e.notes
    if len(notes) > 0:
        element_data.append(
            ("Notes", "<br />\n".join([insert_links(i) for i in notes])))

    # Implementations
    libraries = [
        ("symfem", "Symfem", "https://github.com/mscroggs/symfem", "pip3 install symfem"),
        ("basix", "Basix", "https://github.com/fenics/basix", None),
        ("ufl", "UFL", "https://github.com/fenics/ufl", "pip3 install UFL"),
        ("bempp", "Bempp", "https://github.com/bempp/bempp-cl", None)
    ]
    for codename, libname, url, pip in libraries:
        if e.implemented(codename):
            info = e.list_of_implementation_strings(codename)

            if e.has_implementation_examples(codename):

                info += "<br />"

                info += f"<a class='show_eg_link' id='show_{codename}_link' "
                info += f"href='javascript:show_{codename}_eg()'"
                info += " style='display:block'>"
                info += f"&darr; Show {libname} examples &darr;</a>"
                info += f"<a class='hide_eg_link' id='hide_{codename}_link' "
                info += f"href='javascript:hide_{codename}_eg()'"
                info += " style='display:none'>"
                info += f"&uarr; Hide {libname} examples &uarr;</a>"
                info += f"<div id='{codename}_eg' style='display:none'>"
                info += "Before trying this example, you must install "
                info += f"<a href='{url}'>{libname}</a>"
                if pip is None:
                    info += ". "
                else:
                    info += f":<p class='pcode'>{pip}</p>"
                info += "This element can then be created with the following lines of Python:"

                info += "<p class='pcode'>" + python_highlight(
                    e.make_implementation_examples(codename)) + "</p>"
                info += "</div>"
                info += "<script type='text/javascript'>\n"
                info += f"function show_{codename}_eg(){{\n"
                info += f" document.getElementById('show_{codename}_link').style.display='none'\n"
                info += f" document.getElementById('hide_{codename}_link').style.display='block'\n"
                info += f" document.getElementById('{codename}_eg').style.display='block'\n"
                info += "}\n"
                info += f"function hide_{codename}_eg(){{\n"
                info += f" document.getElementById('show_{codename}_link').style.display='block'\n"
                info += f" document.getElementById('hide_{codename}_link').style.display='none'\n"
                info += f" document.getElementById('{codename}_eg').style.display='none'\n"
                info += "}\n"
                info += "</script>"

            implementations.append((f"{libname}", info))

    # Categories
    cats = e.categories()
    if len(cats) > 0:
        element_data.append(("Categories", ", ".join(cats)))

    # Write element data
    content += "<table class='element-info'>"
    for i, j in element_data:
        content += f"<tr><td>{i.replace(' ', '&nbsp;').replace('<breakable>', ' ')}</td>"
        content += f"<td>{j}</td></tr>"
    content += "</table>"

    # Write implementations
    if len(implementations) > 0:
        content += "<h2>Implementations</h2>\n"
        content += "<table class='element-info'>"
        for i, j in implementations:
            content += f"<tr><td>{i.replace(' ', '&nbsp;')}</td><td>{j}</td></tr>"
        content += "</table>"

    # Write examples using symfem
    element_names = []
    element_examples = []

    if (test_elements is None or e.filename in test_elements) and e.has_examples:
        assert e.implemented("symfem")

        for eg in e.examples:
            cell, order, kwargs = parse_example(eg)
            print(cell, order)
            symfem_name, params = e.get_implementation_string("symfem", cell)

            if "variant" in params:
                element = create_element(cell, symfem_name, order, variant=params["variant"],
                                         **kwargs)
            else:
                element = create_element(cell, symfem_name, order, **kwargs)

            example = markup_example(element)

            if len(example) > 0:
                name = f"{cell}<br />order {order}"
                for i, j in kwargs.items():
                    name += f"<br />{i}={j}"
                element_names.append(name)
                element_examples.append(example)

    if len(element_names) > 0:
        content += "<h2>Examples</h2>\n"
        for i, eg in enumerate(element_names):
            cl = "eglink"
            if i == 0:
                cl += " current"
            content += f"<a class='{cl}' href='javascript:showeg({i})' id='eg{i}'>{eg}</a>"
        for i, eg in enumerate(element_examples):
            cl = "egdetail"
            if i == 0:
                cl += " current"
            content += f"<div class='{cl}' id='egd{i}'>{eg}</div>"

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
    refs = e.references()
    if len(refs) > 0:
        content += "<h2>References</h2>\n"
        content += "<ul class='citations'>\n"
        for i, r in enumerate(refs):
            content += f"<li>{markup_citation(r)}"
            content += f" [<a href='/elements/bibtex/{fname}-{i}.bib'>BibTeX</a>]</li>\n"
            with open(os.path.join(settings.htmlelement_path, f"bibtex/{fname}-{i}.bib"), "w") as f:
                f.write(make_bibtex(f"{fname}-{i}", r))
        content += "</ul>"

    # Write created and updated dates
    if e.created is not None:
        content += "<h2>DefElement stats</h2>\n"
        content += "<table class='element-info'>"
        content += f"<tr><td>Element&nbsp;added</td><td>{e.created.strftime('%d %B %Y')}</td></tr>"
        content += "<tr><td>Element&nbsp;last&nbsp;updated</td>"
        content += f"<td>{e.modified.strftime('%d %B %Y')}</td></tr>"
        content += "</table>"

    # Write file
    with open(os.path.join(settings.htmlelement_path, e.html_filename), "w") as f:
        f.write(make_html_page(content, e.html_name))

# Index page
content = "<h1>Index of elements</h1>\n"
# Generate filtering Javascript
content += "<script type='text/javascript'>\n"
content += "function do_filter_refall(){\n"
content += "    if(document.getElementById('check-ref-all').checked){\n"
for r in categoriser.references:
    content += f"        document.getElementById('check-ref-{r}').checked = false\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter_catall(){\n"
content += "    if(document.getElementById('check-cat-all').checked){\n"
for c in categoriser.categories:
    content += f"        document.getElementById('check-cat-{c}').checked = false\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter_cat(){\n"
content += "    if(document.getElementById('check-cat-all').checked){\n"
content += "        if("
content += " || ".join([f"document.getElementById('check-cat-{c}').checked"
                        for c in categoriser.categories])
content += "){"
content += "            document.getElementById('check-cat-all').checked = false\n"
content += "        }\n"
content += "    }\n"
content += "    do_filter()\n"
content += "}\n"
content += "function do_filter_ref(){\n"
content += "    if(document.getElementById('check-ref-all').checked){\n"
content += "        if("
content += " || ".join([f"document.getElementById('check-ref-{r}').checked"
                        for r in categoriser.references])
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
for r in categoriser.references:

    content += f"            if(document.getElementById('check-ref-{r}').checked"
    content += f" && els[i].id.indexOf('ref-{r}') != -1){{ref_show = true}}\n"
content += "        }\n"
content += "        var cat_show = false\n"
content += "        if(document.getElementById('check-cat-all').checked){\n"
content += "            cat_show = true\n"
content += "        } else {\n"
for c in categoriser.categories:

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
for r in categoriser.references:
    content += f"<label><input type='checkbox' id='check-ref-{r}' onchange='do_filter_ref()'"
    content += f">&nbsp;{r}</label> "
content += "</td></tr>"
content += "<tr><td>Categories</td><td>"
content += "<label><input type='checkbox' checked id='check-cat-all'onchange='do_filter_catall()'"
content += ">&nbsp;show all</label> "
for c in categoriser.categories:
    content += f"<label><input type='checkbox' id='check-cat-{c}'onchange='do_filter_cat()'"
    content += f">&nbsp;{categoriser.get_category_name(c)}</label> "
content += "</td></tr>"
content += "</table>\n"
# Write element list
elementlist = []
for e in categoriser.elements:
    id = " ".join([f"ref-{r}" for r in e.reference_elements(False)]
                  + [f"cat-{c}" for c in e.categories(False, False)])
    for name in [e.html_name] + e.alternative_names(False, False, False, True):
        elementlist.append((name.lower(),
                            f"<li class='element-on-list' id='{id}'>"
                            f"<a href='/elements/{e.html_filename}'>{name}</a></li>"))
elementlist.sort(key=lambda x: x[0])
content += "<ul>" + "\n".join([i[1] for i in elementlist]) + "</ul>"

with open(os.path.join(settings.htmlelement_path, "index.html"), "w") as f:
    f.write(make_html_page(content))
with open(os.path.join(settings.htmlindices_path, "index.html"), "w") as f:
    f.write(make_html_page(content))

# Recently updated elements
content = "<h1>Recent elements</h1>\n"
content += "<h2>Recently added elements</h2>\n"
content += "<ul>\n"
for e in categoriser.recently_added(10):
    content += f"<li><a href='/elements/{e.html_filename}'>{e.html_name}</a>"
    if e.created is not None:
        content += f" ({e.created.strftime('%d %B %Y')})"
    content += "</li>\n"
content += "</ul>\n"

content += "<h2>Recently updated elements</h2>\n"
content += "<ul>\n"
for e in categoriser.recently_updated(10):
    content += f"<li><a href='/elements/{e.html_filename}'>{e.html_name}</a>"
    if e.modified is not None:
        content += f" ({e.modified.strftime('%d %B %Y')})"
    content += "</li>\n"
content += "</ul>\n"

with open(os.path.join(settings.htmlindices_path, "recent.html"), "w") as f:
    f.write(make_html_page(content))

# Category index
os.mkdir(os.path.join(settings.htmlindices_path, "categories"))
content = "<h1>Categories</h1>\n"
for c in categoriser.categories:
    category_pages = []
    for e in categoriser.elements_in_category(c):
        for name in [e.html_name] + e.alternative_names(False, False, False, True):
            category_pages.append((name.lower(),
                                   f"<li><a href='/elements/{e.html_filename}'>{name}</a></li>"))

    category_pages.sort(key=lambda x: x[0])

    content += f"<h2><a name='{c}'>{categoriser.get_category_name(c)}</a></h2>\n<ul>"
    content += "".join([i[1] for i in category_pages])
    content += "</ul>"

    sub_content = f"<h1>{categoriser.get_category_name(c)}</h1>\n<ul>"
    sub_content += "".join([i[1] for i in category_pages])
    sub_content += "</ul>"

    with open(os.path.join(settings.htmlindices_path, f"categories/{c}.html"), "w") as f:
        f.write(make_html_page(sub_content))

with open(os.path.join(settings.htmlindices_path, "categories/index.html"), "w") as f:
    f.write(make_html_page(content))

# Reference elements index
os.mkdir(os.path.join(settings.htmlindices_path, "references"))
content = "<h1>Reference elements</h1>\n"
for c in categoriser.references:
    refels = []
    for e in categoriser.elements_by_reference(c):
        for name in [e.html_name] + e.alternative_names(False, False, False, True, c):
            refels.append((name.lower(),
                           f"<li><a href='/elements/{e.html_filename}'>{name}</a></li>"))

    refels.sort(key=lambda x: x[0])

    content += f"<h2><a name='{c}'></a>{cap_first(c)}</h2>\n"
    content += "<ul>" + "".join([i[1] for i in refels]) + "</ul>"

    sub_content = "<h1>Finite elements on a"
    if c[0] in "aeiou":
        sub_content += "n"
    sub_content += f" {c}</h1>\n"
    sub_content += "<ul>" + "".join([i[1] for i in refels]) + "</ul>"

    with open(os.path.join(settings.htmlindices_path, f"references/{c}.html"), "w") as f:
        f.write(make_html_page(sub_content))

with open(os.path.join(settings.htmlindices_path, "references/index.html"), "w") as f:
    f.write(make_html_page(content))

# Families
content = "<h1>Families</h1>\n"
content += "<ul>\n"
for fname, family in categoriser.exterior_families.items():
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

    with open(os.path.join(settings.htmlfamilies_path, f"{fname}.html"), "w") as f:
        f.write(make_html_page(sub_content))

    content += f"<li><a href='/families/{fname}.html'>\\({tex_name}^r\\)</a></li>\n"
content += "</ul>"
with open(os.path.join(settings.htmlfamilies_path, "index.html"), "w") as f:
    f.write(make_html_page(content))

# List of lists
content = "<h1>Lists of elements</h1>\n<ul>\n"
content += "<li><a href='/lists/categories'>Finite elements by category</a></li>\n"
content += "<li><a href='/lists/references'>Finite elements by reference element</a></li>\n"
content += "<li><a href='/lists/recent.html'>Recently added/updated finite elements</a></li>\n"
content += "</ul>"
with open(os.path.join(settings.htmlindices_path, "index.html"), "w") as f:
    f.write(make_html_page(content))
