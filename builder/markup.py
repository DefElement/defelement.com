import shlex
import re
from datetime import datetime
from citations import markup_citation
import symbols

page_references = []


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

    out = re.sub(r"`([^`]+)`", r"<span style='font-family:monospace'>\1</span>", out)

    if len(page_references) > 0:
        out += "<h2>References</h2>"
        out += "<ul class='citations'>"
        out += "".join([f"<li><a class='refid' id='ref{i+1}'>[{i+1}]</a> {j}</li>"
                        for i, j in enumerate(page_references)])
        out += "</ul>"

    return insert_dates(out)


def insert_links(txt):
    txt = re.sub(r"\(element::([^\)]+)\)", r"(/elements/\1.html)", txt)
    txt = txt.replace("(index::all)", "(/elements/index.html)")
    txt = txt.replace("(index::families)", "(/families/index.html)")
    txt = re.sub(r"\(index::([^\)]+)::([^\)]+)\)", r"(/lists/\1/\2.html)", txt)
    txt = re.sub(r"\(index::([^\)]+)\)", r"(/lists/\1)", txt)
    txt = re.sub(r"\(([^\)]+)\.md\)", r"(/\1.html)", txt)
    txt = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r"<a href='\2'>\1</a>", txt)
    return txt


def plot_element(matches):
    from elements import draw_function
    import symfem
    if "variant=" in matches[1]:
        a, b = matches[1].split(" variant=")
        e = symfem.create_element(a, matches[2], int(matches[3]), b)
    else:
        e = symfem.create_element(matches[1], matches[2], int(matches[3]))
    return f"<center>{''.join([draw_function(e, i) for i in range(e.space_dim)])}</center>"


def plot_single_element(matches):
    from elements import draw_function
    import symfem
    if "variant=" in matches[1]:
        a, b = matches[1].split(" variant=")
        e = symfem.create_element(a, matches[2], int(matches[3]), b)
    else:
        e = symfem.create_element(matches[1], matches[2], int(matches[3]))
    return f"<center>{draw_function(e, int(matches[4]))}</center>"


def plot_reference(matches):
    from elements import svg_reference
    import symfem
    e = symfem.create_reference(matches[1])
    return f"<center>{svg_reference(e)}</center>"


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
