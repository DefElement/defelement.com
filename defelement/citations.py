"""Citations."""

import re
import typing


def markup_authors(a: typing.Union[str, typing.List[str]]) -> str:
    """Markup authors.

    Args:
        a: Authors

    Returns:
        Formatted list of authors
    """
    if isinstance(a, str):
        return a
    else:
        if len(a) == 2:
            return a[0] + " and " + a[1]
        else:
            return ", ".join(a[:-1]) + ", and " + a[-1]


def markup_citation(r: typing.Dict[str, typing.Any]) -> str:
    """Markup citations.

    Args:
        r: Citation

    Returns:
        Formatted citation
    """
    out = ""
    if "author" in r:
        out += markup_authors(r["author"])
    else:
        out += "<i>(unknown author)</i>"
    if out[-1] != ".":
        out += "."
    out += f" {r['title']}"
    if "journal" in r:
        out += f", <em>{r['journal']}</em>"
        if "volume" in r:
            out += f" {r['volume']}"
            if "issue" in r:
                out += f"({r['issue']})"
        if "pagestart" in r and "pageend" in r:
            out += f", {r['pagestart']}&ndash;{r['pageend']}"
    elif "arxiv" in r:
        out += f", ar&Chi;iv: <a href='https://arxiv.org/abs/{r['arxiv']}'>{r['arxiv']}</a>"
    if "booktitle" in r:
        out += f", in <em>{r['booktitle']}</em>"
        if "editor" in r:
            out += f" (eds: {markup_authors(r['editor'])})"
    if "year" in r:
        out += f", {r['year']}"
    out += "."
    if "doi" in r:
        out += f" [DOI:&nbsp;<a href='https://doi.org/{r['doi']}'>{r['doi']}</a>]"
    if "url" in r:
        out += f" [<a href='{r['url']}'>{r['url'].split('://')[1]}</a>]"
    return out


def wrap_caps(txt: str) -> str:
    """Wrap capitials in curly braces.

    Args:
        txt: Input string

    Returns:
        String with capitals wrapped in curly braces
    """
    return re.sub(r"([A-Z])", r"{\1}", txt)


def html_to_tex(txt: str) -> str:
    """Convert html to TeX.

    Args:
        txt: HTML

    Returns:
        TeX
    """
    txt = re.sub(r"&([A-Za-z])acute;", r"\\'\1", txt)
    txt = re.sub(r"&([A-Za-z])uml;", r"\\\"\1", txt)
    txt = re.sub(r"&([A-Za-z])cedil;", r"\\c{\1}", txt)
    txt = txt.replace("&ndash;", "--")
    txt = txt.replace("&mdash;", "---")
    return txt


def make_bibtex(id: str, r: typing.Dict[str, typing.Any]) -> str:
    """Make BibTex.

    Args:
        id: Unique identifier
        r: A citation

    Returns:
        The citation in BibTeX format
    """
    if 'type' not in r:
        r["type"] = "article"
    out = f"@{r['type']}{{{id},\n"

    # Author-type fields
    for i, j in [("AUTHOR", "author"), ("EDITOR", "editor")]:
        if j in r:
            out += " " * (10 - len(i)) + f"{i} = {{"
            if isinstance(r[j], str):
                out += wrap_caps(html_to_tex(r[j]))
            else:
                out += " and ".join([wrap_caps(html_to_tex(k)) for k in r[j]])
            out += "},\n"

    # Fields with caps that need wrapping
    for i, j in [("TITLE", "title"), ("BOOKTITLE", "booktitle")]:
        if j in r:
            out += " " * (10 - len(i)) + f"{i} = {{{wrap_caps(html_to_tex(r[j]))}}},\n"

    # Text fields
    for i, j in [("JOURNAL", "journal")]:
        if j in r:
            out += " " * (10 - len(i)) + f"{i} = {{{html_to_tex(r[j])}}},\n"

    # Numerical fields
    for i, j in [
        ("VOLUME", "volume"), ("NUMBER", "issue"),
        ("YEAR", "year"), ("DOI", "doi")
    ]:
        if j in r:
            out += " " * (10 - len(i)) + f"{i} = {{{r[j]}}},\n"

    # Page numbers
    if "pagestart" in r and "pageend" in r:
        out += f"     PAGES = {{{{{r['pagestart']}--{r['pageend']}}}}},\n"
    out += "}"
    return out
