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
        else:
            if not popen and not line.startswith("<") and not line.startswith("\\["):
                if code:
                    out += "<p style='margin-left:50px;margin-right:50px;font-family:monospace'>"
                else:
                    out += "<p>"
                popen = True
            if code:
                out += line.replace(" ", "&nbsp;")
                out += "<br />"
            else:
                out += line
                out += " "
    page_references = []
    out = re.sub(r" *<ref ([^>]+)>", add_citation, out)
    out = re.sub(r"\(element::([^\)]+)\)", r"(/elements/\1.html)", out)
    out = re.sub(r"\(([^\)]+)\.md\)", r"(/\1.html)", out)
    out = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r"<a href='\2'>\1</a>", out)

    out = re.sub(r"{{plot::([^,]+),([^,]+),([1-9][0-9]*)}}", plot_element, out)

    if len(page_references) > 0:
        out += "<h2>References</h2>"
        out += "<ul class='citations'>"
        out += "".join([f"<li><a class='refid' id='ref{i+1}'>[{i+1}]</a> {j}</li>"
                        for i, j in enumerate(page_references)])
        out += "</ul>"

    return insert_dates(out)


def plot_element(matches):
    from elements import markup_element
    import symfem
    e = symfem.create_element(matches[1], matches[2], int(matches[3]))
    return f"<center>{markup_element(e, True)}</center>"


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
    txt = re.sub("{{symbols\.([^}]+)}}", lambda m: getattr(symbols, m[1]), txt)

    return txt
