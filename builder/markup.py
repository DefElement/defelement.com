import os
import re
import shlex
import symfem
import yaml
from datetime import datetime
from . import symbols
from . import plotting
from . import settings
from .citations import markup_citation

page_references = []


def cap_first(txt):
    return txt[:1].upper() + txt[1:]


def list_contributors():
    with open(os.path.join(settings.data_path, "contributors")) as f:
        people = yaml.load(f, Loader=yaml.FullLoader)
    out = ""
    for info in people:
        if "img" in info:
            out += f"<img src='/img/people/{info['img']}' class='person'>"
        out += f"<h2>{info['name']}</h2>"
        if "desc" in info:
            out += f"<p>{markup(info['desc'])}</p>"
        out += "<ul class='person-info'>"
        if "website" in info:
            website_name = info["website"].split("//")[1].strip("/")
            out += (f"<li><a href='{info['website']}'>"
                    "<i class='fa fa-internet-explorer' aria-hidden='true'></i>"
                    f"&nbsp;{website_name}</a></li>")
        if "twitter" in info:
            out += (f"<li><a href='https://twitter.com/{info['twitter']}'>"
                    "<i class='fa fa-twitter' aria-hidden='true'></i>"
                    f"&nbsp;@{info['twitter']}</a></li>")
        if "github" in info:
            out += (f"<li><a href='https://github.com/{info['github']}'>"
                    "<i class='fa fa-github' aria-hidden='true'></i>"
                    f"&nbsp;{info['github']}</a></li>")
        out += "</ul>"
        out += "<br style='clear:both' />"
    return out


def markup(content):
    global page_references
    out = ""
    popen = False
    code = False
    is_python = False

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
        elif line == "```":
            code = not code
            is_python = False
        elif line == "```python":
            code = not code
            is_python = True
        else:
            if not popen and not line.startswith("<") and not line.startswith("\\["):
                if code:
                    out += "<p class='pcode'>"
                else:
                    out += "<p>"
                popen = True
            if code:
                if is_python:
                    out += python_highlight(line.replace(" ", "&nbsp;"))
                else:
                    out += line.replace(" ", "&nbsp;")
                out += "<br />"
            else:
                out += line
                out += " "

    page_references = []

    out = re.sub(r" *<ref ([^>]+)>", add_citation, out)

    out = insert_links(out)
    out = re.sub(r"{{plot::([^,]+),([^,]+),([0-9]+)}}", plot_element, out)
    out = re.sub(r"{{plot::([^,]+),([^,]+),([0-9]+)::([0-9]+)}}",
                 plot_single_element, out)
    out = re.sub(r"{{reference::([^}]+)}}", plot_reference, out)

    out = re.sub(r"{{img::([^}]+)}}", plot_img, out)

    out = re.sub(r"`([^`]+)`", r"<span style='font-family:monospace'>\1</span>", out)

    out = out.replace("{{tick}}", "<i class='fa-solid fa-check' style='color:#55ff00'></i>")
    if "{{list contributors}}" in out:
        out = out.replace("{{list contributors}}", list_contributors())

    if len(page_references) > 0:
        out += "<h2>References</h2>"
        out += "<ul class='citations'>"
        out += "".join([f"<li><a class='refid' id='ref{i+1}'>[{i+1}]</a> {j}</li>"
                        for i, j in enumerate(page_references)])
        out += "</ul>"

    return insert_dates(out)


def insert_links(txt):
    txt = re.sub(r"\(element::([^\)]+)\)", r"(/elements/\1.html)", txt)
    txt = re.sub(r"\(reference::([^\)]+)\)", r"(/lists/references/\1.html)", txt)
    txt = txt.replace("(index::all)", "(/elements/index.html)")
    txt = txt.replace("(index::families)", "(/families/index.html)")
    txt = txt.replace("(index::recent)", "(/lists/recent.html)")
    txt = re.sub(r"\(index::([^\)]+)::([^\)]+)\)", r"(/lists/\1/\2.html)", txt)
    txt = re.sub(r"\(index::([^\)]+)\)", r"(/lists/\1)", txt)
    txt = re.sub(r"\(([^\)]+)\.md\)", r"(/\1.html)", txt)
    txt = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r"<a href='\2'>\1</a>", txt)
    return txt


def plot_element(matches):
    if "variant=" in matches[1]:
        a, b = matches[1].split(" variant=")
        e = symfem.create_element(a, matches[2], int(matches[3]), b)
    else:
        e = symfem.create_element(matches[1], matches[2], int(matches[3]))
    return ("<center>"
            f"{''.join([plotting.plot_function(e, i).img_html() for i in range(e.space_dim)])}"
            "</center>")


def plot_single_element(matches):
    if "variant=" in matches[1]:
        a, b = matches[1].split(" variant=")
        e = symfem.create_element(a, matches[2], int(matches[3]), b)
    else:
        e = symfem.create_element(matches[1], matches[2], int(matches[3]))
    return f"<center>{plotting.plot_function(e, int(matches[4])).img_html()}</center>"


def plot_reference(matches):
    e = symfem.create_reference(matches[1])
    return f"<center>{plotting.plot_reference(e).img_html()}</center>"


def plot_img(matches):
    e = matches[1]
    return f"<center>{plotting.plot_img(e).img_html()}</center>"


def add_citation(matches):
    global page_references
    ref = {}
    for i in shlex.split(matches[1]):
        a, b = i.split("=")
        ref[a] = b
    page_references.append(markup_citation(ref))
    return f"<sup><a href='#ref{len(page_references)}'>[{len(page_references)}]</a></sup>"


def insert_dates(txt):
    now = datetime.now()
    txt = txt.replace("{{date:Y}}", now.strftime("%Y"))
    txt = txt.replace("{{date:D-M-Y}}", now.strftime("%d-%B-%Y"))
    txt = re.sub("{{symbols\\.([^}\\(]+)\\(([0-9]+)\\)}}",
                 lambda m: getattr(symbols, m[1])(int(m[2])), txt)
    txt = re.sub("{{symbols\\.([^}]+)}}", lambda m: getattr(symbols, m[1]), txt)

    return txt


def python_highlight(txt):
    txt = txt.replace(" ", "&nbsp;")
    out = []
    for line in txt.split("\n"):
        comment = ""
        if "#" in line:
            lsp = line.split("#", 1)
            line = lsp[0]
            comment = f"<span style='color:#FF8800'>#{lsp[1]}</span>"

        lsp = line.split("\"")
        line = lsp[0]

        for i, j in enumerate(lsp[1:]):
            if i % 2 == 0:
                line += f"<span style='color:#DD2299'>\"{j}"
            else:
                line += f"\"</span>{j}"

        out.append(line + comment)
    return "<br />".join(out)
