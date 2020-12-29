import re


def markup_citation(r):
    out = ""
    if "author" in r:
        out += r["author"]
    else:
        out += "<i>(unknown author)</i>"
    out += f" {r['title']}"
    if "journal" in r:
        out += f", <em>{r['journal']}</em>"
        if "volume" in r:
            out += f" {r['volume']}"
            if "issue" in r:
                out += f"({r['issue']})"
        if "pagestart" in r and "pageend" in r:
            out += f", {r['pagestart']}&ndash;{r['pageend']}"
    if "year" in r:
        out += f", {r['year']}"
    out += "."
    if "doi" in r:
        out += f" [DOI:&nbsp;<a href='https://doi.org/{r['doi']}'>{r['doi']}</a>]"
    return out


def wrap_caps(txt):
    txt = re.sub(r"&([A-Za-z])acute;", r"\\'\1", txt)
    txt = re.sub(r"&([A-Za-z])uml;", r"\\\"\1", txt)
    txt = re.sub(r"([A-Z])", r"{\1}", txt)
    return txt


def make_bibtex(id, r):
    if 'type' not in r:
        r["type"] = "article"
    out = f"@{{r['type']}}{{{id},\n"
    for i, j in [
        ("AUTHOR", "author"), ("TITLE", "title"),
    ]:
        if j in r:
            out += " " * (10 - len(i)) + f"{i} = {{{wrap_caps(r[j])}}},\n"
    for i, j in [
        ("JOURNAL", "journal"), ("VOLUME", "volume"), ("NUMBER", "issue"),
        ("YEAR", "year"), ("DOI", "doi")
    ]:
        if j in r:
            out += " " * (10 - len(i)) + f"{i} = {{{r[j]}}},\n"
    if "pagestart" in r and "pageend" in r:
        out += f"     PAGES = {{{{{r['pagestart']}--{r['pageend']}}}}},\n"
    out += "}"
    return out
