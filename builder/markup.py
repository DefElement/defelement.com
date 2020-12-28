import re
from datetime import datetime


def markup(content):
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
            if not popen:
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

    out = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r"<a href='\2'>\1</a>", out)

    return insert_dates(out)


def insert_dates(txt):
    now = datetime.now()
    txt = txt.replace("{{date:Y}}", now.strftime("%Y"))
    txt = txt.replace("{{date:D-M-Y}}", now.strftime("%d-%B-%Y"))

    return txt
