import os
import sympy
import typing
from datetime import datetime
from symfem.plotting import Picture, colors
from . import settings

now = datetime.now()
svg_desc = (
   "This plot is from DefElement (https://defelement.com) "
   "and is available under a Creative Commons Attribution "
   "4.0 International (CC BY 4.0) license: "
   "https://creativecommons.org/licenses/by/4.0/")
svg_metadata = (
    "<metadata id='license'>\n"
    " <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' "
    "xmlns:dc='http://purl.org/dc/elements/1.1/' "
    "xmlns:cc='http://web.resource.org/cc/'>\n"
    "   <cc:Work rdf:about=''>\n"
    "     <dc:title>{title}</dc:title>\n"
    f"     <dc:date>{now.strftime('%Y-%m-%d')}</dc:date>\n"
    "     <dc:creator>\n"
    "       <cc:Agent><dc:title>DefElement</dc:title></cc:Agent>\n"
    "       <cc:Agent><dc:title>Matthew Scroggs</dc:title></cc:Agent>\n"
    "     </dc:creator>\n"
    "     <dc:description>See document description</dc:description>\n"
    "     <cc:license rdf:resource='http://creativecommons.org/licenses/by/4.0/'/>\n"
    "     <dc:format>image/svg+xml</dc:format>\n"
    "     <dc:type rdf:resource='http://purl.org/dc/dcmitype/StillImage'/>\n"
    "   </cc:Work>\n"
    "   <cc:License rdf:about='http://creativecommons.org/licenses/by/4.0/'>\n"
    "     <cc:permits rdf:resource='http://web.resource.org/cc/Reproduction'/>\n"
    "     <cc:permits rdf:resource='http://web.resource.org/cc/Distribution'/>\n"
    "     <cc:permits rdf:resource='http://web.resource.org/cc/DerivativeWorks'/>\n"
    "     <cc:requires rdf:resource='http://web.resource.org/cc/Notice'/>\n"
    "     <cc:requires rdf:resource='http://web.resource.org/cc/Attribution'/>\n"
    "   </cc:License>\n"
    " </rdf:RDF>\n"
    "</metadata>\n")
tex_comment = (
    "% -------------------------------------------------------\n"
    "% This plot is from DefElement (https://defelement.com)\n"
    "% and is available under a Creative Commons Attribution\n"
    "% 4.0 International (CC BY 4.0) license:\n"
    "% https://creativecommons.org/licenses/by/4.0/\n"
    "% -------------------------------------------------------\n")

all_plots = []


def do_the_plot(
    filename: str, desc: str, plot: typing.Callable,
    args: typing.List[typing.Any] = [], png_width: int = 180,
) -> str:
    global all_plots
    from .html import make_html_page
    from .markup import cap_first

    kwargs = {
        "title": desc, "desc": svg_desc,
        "svg_metadata": svg_metadata.replace("{title}", desc), "tex_comment": tex_comment}
    svg_kw = {"scale": 250, "dof_arrow_size": sympy.Rational(3, 2)}

    if filename not in all_plots:
        plot(*args, os.path.join(settings.htmlimg_path, f"{filename}.tex"), **kwargs)
        plot(*args, os.path.join(settings.htmlimg_path, f"{filename}.svg"), **svg_kw, **kwargs)
        plot(*args, os.path.join(settings.htmlimg_path, f"{filename}.png"),
             plot_options={"png_width": png_width}, **svg_kw, **kwargs)
        plot(*args, os.path.join(settings.htmlimg_path, f"{filename}-large.png"),
             plot_options={"png_width": png_width * 9 // 2}, **svg_kw, **kwargs)

        img_page = f"<h1>{cap_first(desc)}</h1>\n"
        img_page += f"<center><a href='/img/{filename}-large.png'>"
        img_page += f"<img src='/img/{filename}.png'></a></center>\n"

        img_page += ("<p>"
                     "This image can be used under a "
                     "<a href='https://creativecommons.org/licenses/by/4.0/'>"
                     "Creative Commons Attribution 4.0 International (CC BY 4.0) license"
                     "</a>: if you use it anywhere, you must attribute DefElement. "
                     "If you use this image anywhere online, please include a link to "
                     "DefElement; if you use this image in a paper, please <a href='"
                     "/citing.html'>cite DefElement</a>."
                     "</p>")
        img_page += "<ul>"
        img_page += f"<li><a href='/img/{filename}-large.png'>Download PNG</a></li>"
        img_page += f"<li><a href='/img/{filename}.svg'>Download SVG</a></li>"
        img_page += f"<li><a href='/img/{filename}.tex'>Download TikZ</a></li>"
        img_page += "</ul>"

        with open(os.path.join(settings.htmlimg_path, f"{filename}.html"), "w") as f:
            f.write(make_html_page(img_page))
        all_plots.append(filename)

    return f"<a href='/img/{filename}.html'><img src='/img/{filename}.png'></a>"


def plot_reference(ref):
    if ref.name == "dual polygon":
        ref_id = f"dual-polygon-{ref.number_of_triangles}"
    else:
        ref_id = ref.name

    filename = f"ref-{ref_id}"
    desc = f"{ref.name} reference element"

    return do_the_plot(filename, desc, ref.plot_entity_diagrams, png_width=600)


def plot_function(element, dof_i):
    if element.reference.name == "dual polygon":
        ref_id = f"dual-polygon-{element.reference.number_of_triangles}"
    else:
        ref_id = element.reference.name

    desc = f"Basis function in a {element.name} space"
    return do_the_plot(f"element-{element.name}-{ref_id}-{element.order}-{dof_i}", desc,
                       element.plot_basis_function, [dof_i])


def plot_basis_functions(element):
    if element.range_dim == 1:
        if element.domain_dim > 2:
            return [None for i in range(element.space_dim)]
    else:
        if element.range_dim != element.domain_dim:
            return [None for i in range(element.space_dim)]

    return [plot_function(element, i) for i in range(element.space_dim)]


def _parse_point(points, n):
    point = points[n].strip()
    if point == "cycle":
        assert n > 0
        return _parse_point(points, 0)
    assert point[0] == "(" and point[-1] == ")"

    x, y = point[1:-1].split(",")
    return float(x) / 100, float(y) / 100


def plot_img(img_filename: str):
    metadata = {"DESC": ""}
    filename = f"img-{img_filename}"
    with open(os.path.join(settings.img_path, f"{img_filename}.img")) as f:
        for line in f:
            if ":" in f:
                a, b = f.split(":", 1)
                metadata[a.strip()] = b.strip()
    desc = metadata["DESC"]

    def actual_plot(
        filename: str, plot_options: typing.Dict[str, typing.Any] = {}, **kwargs: typing.Any
    ):
        img = Picture(**kwargs)
        with open(os.path.join(settings.img_path, f"{img_filename}.img")) as f:
            for line in f:
                if ":" not in line:
                    line = line.split("#")[0]
                    line = line.strip()
                    color = "black"
                    if line.startswith("["):
                        color, line = line[1:].split("]", 1)
                        line = line.strip()
                    if hasattr(colors, color.upper()):
                        color = getattr(colors, color.upper())

                    points = line.split("--")
                    for i in range(len(points) - 1):
                        p1 = _parse_point(points, i)
                        p2 = _parse_point(points, i + 1)
                        img.add_line(p1, p2, color=color, width=2)
        img.save(filename, plot_options)

    return do_the_plot(filename, desc, actual_plot)
