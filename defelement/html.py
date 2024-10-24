"""HTML tools."""

import os
import typing

from defelement import settings
from defelement.markup import insert_dates


def make_html_page(content: str, pagetitle: typing.Optional[str] = None) -> str:
    """Make a HTML page.

    Args:
        content: Page content
        pagetitle: Page title

    Return:
        Formatted HTML page
    """
    out = ""
    with open(os.path.join(settings.template_path, "intro.html")) as f:
        out += insert_dates(f.read())
    if pagetitle is None:
        out = out.replace("{{: pagetitle}}", "")
        out = out.replace("{{pagetitle |}}", "")
    else:
        out = out.replace("{{: pagetitle}}", f": {pagetitle}")
        out = out.replace("{{pagetitle |}}", f"{pagetitle} |")
    out += content
    with open(os.path.join(settings.template_path, "outro.html")) as f:
        out += insert_dates(f.read())
    return out
