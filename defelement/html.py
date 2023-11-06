import os
from . import settings
from .markup import insert_dates


def make_html_page(content, pagetitle=None):
    out = ""
    with open(os.path.join(settings.template_path, "intro.html")) as f:
        out += insert_dates(f.read())
    if pagetitle is None:
        out = out.replace("{{: pagetitle}}", "")
    else:
        out = out.replace("{{: pagetitle}}", f": {pagetitle}")
    out += content
    with open(os.path.join(settings.template_path, "outro.html")) as f:
        out += insert_dates(f.read())
    return out
