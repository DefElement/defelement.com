"""Markup."""

import os
import re
import shlex
import typing
import warnings
from datetime import datetime
from urllib.parse import quote_plus

import symfem
import yaml
from github import Github

from defelement import plotting, settings, symbols
from defelement.tools import comma_and_join

page_references: typing.List[str] = []


def cap_first(txt: str) -> str:
    """Captialise first letter.

    Args:
        txt: Input text

    Returns:
        text with capitalised first letter
    """
    return txt[:1].upper() + txt[1:]


def heading_with_self_ref(hx: str, content: str, style: typing.Optional[str] = None) -> str:
    """Create heading with self reference.

    Args:
        hx: HTML tag
        content: Heading content

    Returns:
        Heading with self reference
    """
    id = quote_plus(content)
    out = f"<{hx} id=\"{id}\""
    if style is not None:
        out += f" style=\"{style}\""
    out += f"><a href=\"#{id}\">{content}</a></{hx}>\n"
    return out


def format_names(names: typing.List[str], format: str) -> str:
    """Format names.

    Args:
        names: List of names
        format: Format. `bibtex`, `html`, and `citation` are allowed

    Returns:
        Formatted names
    """
    if format == "bibtex":
        return " and ".join(names)
    else:
        formatted_names = []
        for n in names:
            if n == "et al":
                formatted_names.append("et al")
            else:
                nsp = n.split(", ")
                name = ""
                for i in nsp[:0:-1]:
                    for j in i.split(" "):
                        name += f"{j[0]}. "
                name += nsp[0]
                formatted_names.append(name)
        if names[-1] == "et al":
            if len(formatted_names) <= 2:
                return " ".join(formatted_names)
            else:
                return ", ".join([", ".join(formatted_names[:-1]), formatted_names[-1]])
        else:
            return comma_and_join(formatted_names)


def person_sort_key(p: typing.Dict):
    """Key used to sort people for the contributors and citation lists."""
    with open(os.path.join(settings.data_path, "editors")) as f:
        editors = yaml.load(f, Loader=yaml.FullLoader)
    if "github" in p:
        if p["github"] == "mscroggs":
            return "AAA"
        if p in editors:
            return "AAB" + p["name"]
    return p["name"]


def list_contributors(format: str = "html") -> str:
    """Get list of contributors.

    Args:
        format: Format. `bibtex`, `html`, and `citation` are allowed

    Returns:
        Contributor list
    """
    if format not in ["html", "bibtex", "citation"]:
        raise ValueError(f"Unsupported format: {format}")

    with open(os.path.join(settings.data_path, "contributors")) as f:
        people = yaml.load(f, Loader=yaml.FullLoader)
    people.sort(key=person_sort_key)
    with open(os.path.join(settings.data_path, "editors")) as f:
        editors = yaml.load(f, Loader=yaml.FullLoader)

    if format == "html":
        included = []
        out = ""

        editors_out = ""
        contributors_out = ""
        for info in people:
            person_out = ""
            if "img" in info:
                person_out += f"<img src='/img/people/{info['img']}' class='person'>"
            person_out += heading_with_self_ref("h2", " ".join(info["name"].split(", ")[::-1]))
            if "desc" in info:
                person_out += f"<p>{markup(info['desc'])}</p>"
            if "website" in info:
                website_name = info["website"].split("//")[1].strip("/")
                person_out += (f"<div class='social'><a href='{info['website']}'>"
                               "<i class='fa-brands fa-internet-explorer' aria-hidden='true'></i>"
                               f"&nbsp;{website_name}</a></div>")
            if "email" in info:
                person_out += (f"<div class='social'><a href='mailto:{info['email']}'>"
                               "<i class='fa-regular fa-envelope' aria-hidden='true'></i>"
                               f"&nbsp;{info['email']}</a></div>")
            if "github" in info:
                person_out += (f"<div class='social'><a href='https://github.com/{info['github']}'>"
                               "<i class='fa-brands fa-github' aria-hidden='true'></i>"
                               f"&nbsp;{info['github']}</a></div>")
                included.append(info["github"])
            if "twitter" in info:
                person_out += (
                    f"<div class='social'><a href='https://twitter.com/{info['twitter']}'>"
                    "<i class='fa-brands fa-twitter' aria-hidden='true'></i>"
                    f"&nbsp;@{info['twitter']}</a></div>"
                )
            if "mastodon" in info:
                handle, url = info["mastodon"].split("@")
                person_out += (f"<div class='social'><a href='https://{url}/@{handle}'>"
                               "<i class='fa-brands fa-mastodon' aria-hidden='true'></i>"
                               f"&nbsp;@{handle}@{url}</a></div>")
            person_out += "<br style='clear:both' />"
            if "github" in info and info["github"] in editors:
                editors_out += person_out
            else:
                contributors_out += person_out

        if editors != "":
            out += heading_with_self_ref("h1", "Editors", "margin-top:50px")
            out += (
                "<p>The contributors listed in this section are responsible for reviewing "
                f"contributions to DefElement.</p>\n{editors_out}"
            )
            out += heading_with_self_ref("h1", "Contributors", "margin-top:50px")
        out += contributors_out

        if settings.github_token is None:
            warnings.warn("Building without GitHub token. Skipping search for GitHub contributors.")
        else:
            g = Github(settings.github_token)
            repo = g.get_repo("DefElement/defelement.com")
            pages = repo.get_contributors()
            i = 0
            extras = []
            while True:
                page = pages.get_page(i)
                if len(page) == 0:
                    break
                for user in page:
                    if user.login not in included:
                        extras.append((user.login, user.name))
                i += 1
            if len(extras) > 0:
                out += heading_with_self_ref("h2", "Additional contributors")
                out += ("<p>The following people have contributed to DefElement but are yet to add "
                        "details about themselves to this page:</p>\n<ul>\n")
                for u in extras:
                    out += "<li>"
                    if u[1] is not None:
                        out += f"{u[1]} ("
                    out += (f"<a href='https://github.com/{u[0]}'>"
                            "<i class='fa-brands fa-github' aria-hidden='true'></i>"
                            f"&nbsp;{u[0]}</a>")
                    if u[1] is not None:
                        out += ")"
                    out += "</li>\n"
                out += "</ul>"
                out += ("<p>If you're listed here, you can find instructions for how to add "
                        "information about yourself on the [contributing page](contributing.md"
                        "#Adding+yourself+to+the+contributors+list).</p>")

        return out
    else:
        names = []
        for info in people:
            names.append(info["name"])

        if settings.github_token is None:
            warnings.warn(
                "Building without GitHub token. Skipping search for GitHub contributors.")
        else:
            included = [info["github"] for info in people if "github" in info]
            g = Github(settings.github_token)
            repo = g.get_repo("DefElement/defelement.com")
            pages = repo.get_contributors()
            i = 0
            while True:
                page = pages.get_page(i)
                if len(page) == 0:
                    break
                for user in page:
                    if user.login not in included:
                        if format == "bibtex":
                            names.append("others")
                        else:
                            names.append("et al")
                        break
                else:
                    i += 1
                    continue
                break

        return format_names(names, format)


def preprocess(content: str) -> str:
    """Preprocess content.

    Args:
        content: Content

    Returns:
        Preprocessed content
    """
    for file in os.listdir(settings.dir_path):
        if file.endswith(".md"):
            if f"{{{{{file}}}}}" in content:
                with open(os.path.join(settings.dir_path, file)) as f:
                    content = content.replace(
                        f"{{{{{file}}}}}",
                        f.read().replace("](https://defelement.com", "]("))

    if "{{list contributors}}" in content:
        content = content.replace("{{list contributors}}", list_contributors())
    if "{{list contributors|" in content:
        content = re.sub("{{list contributors\\|([^}]+)}}",
                         lambda matches: list_contributors(matches[1]), content)
    content = re.sub(r"{{author-info::([^}]+)}}", author_info, content)
    return content


def markup(content: str) -> str:
    """Markup content.

    Args:
        content: Content

    Returns:
        Content with markup replaced by HTML
    """
    global page_references

    content = preprocess(content)

    out = ""
    popen = False
    ulopen = False
    liopen = False
    code = False
    is_python = False
    is_bash = False

    for line in content.split("\n"):
        if line.startswith("#"):
            if popen:
                out += "</p>\n"
                popen = False
            if ulopen:
                if liopen:
                    out += "</li>"
                    liopen = False
                out += "</ul>\n"
                ulopen = False
            i = 0
            while line.startswith("#"):
                line = line[1:]
                i += 1
            out += heading_with_self_ref(f"h{i}", line.strip())
        elif line.startswith("* "):
            if popen:
                out += "</p>\n"
                popen = False
            if not ulopen:
                out += "<ul>"
                ulopen = True
            if liopen:
                out += "</li>"
                liopen = False
            out += "<li>"
            liopen = True
            out += line[2:].strip()
        elif line == "":
            if popen:
                out += "</p>\n"
                popen = False
            if ulopen:
                if liopen:
                    out += "</li>"
                    liopen = False
                out += "</ul>\n"
                ulopen = False
        elif line == "```":
            code = not code
            is_python = False
            is_bash = False
        elif line == "```python":
            code = not code
            is_python = True
            is_bash = False
        elif line == "```bash":
            code = not code
            is_python = False
            is_bash = True
        else:
            if not ulopen and not popen and not line.startswith("<") and not line.startswith("\\["):
                if code:
                    out += "<p class='pcode'>"
                else:
                    out += "<p>"
                popen = True
            if code:
                if is_python:
                    out += python_highlight(line.replace(" ", "&nbsp;"))
                elif is_bash:
                    out += bash_highlight(line.replace(" ", "&nbsp;"))
                else:
                    out += line.replace(" ", "&nbsp;")
                out += "<br />"
            else:
                out += line
                out += " "

    page_references = []

    out = out.replace("(CODE_OF_CONDUCT.md)", "(code-of-conduct.md)")

    out = re.sub(r" *<ref ([^>]+)>", add_citation, out)

    out = insert_links(out)
    out = re.sub(r"{{code-include::([^}]+)}}", code_include, out)
    out = re.sub(r"{{plot::([^,]+),([^,]+),([0-9]+)}}", plot_element, out)
    out = re.sub(r"{{plot::([^,]+),([^,]+),([0-9]+)::([0-9]+)}}",
                 plot_single_element, out)
    out = re.sub(r"{{reference::([^}]+)}}", plot_reference, out)

    out = re.sub(r"{{img::([^}]+)}}", plot_img, out)

    out = re.sub(r"`([^`]+)`", r"<span style='font-family:monospace'>\1</span>", out)

    out = re.sub(r"\*\*([^\n]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\*([^\n]+)\*", r"<em>\1</em>", out)

    out = out.replace("{{tick}}", "<i class='fa-solid fa-check' style='color:#55ff00'></i>")

    if len(page_references) > 0:
        out += heading_with_self_ref("h2", "References")
        out += "<ul class='citations'>"
        out += "".join([f"<li><a class='refid' id='ref{i+1}'>[{i+1}]</a> {j}</li>"
                        for i, j in enumerate(page_references)])
        out += "</ul>"

    return insert_dates(out)


def insert_links(txt: str) -> str:
    """Insert links.

    Args:
        txt: text

    Returns:
        Text with links
    """
    txt = re.sub(r"\(element::([^\)]+)\)", r"(/elements/\1.html)", txt)
    txt = re.sub(r"\(reference::([^\)]+)\)", r"(/lists/references/\1.html)", txt)
    txt = txt.replace("(index::all)", "(/elements/index.html)")
    txt = txt.replace("(index::families)", "(/families/index.html)")
    txt = txt.replace("(index::recent)", "(/lists/recent.html)")
    txt = re.sub(r"\(index::([^\)]+)::([^\)]+)\)", r"(/lists/\1/\2.html)", txt)
    txt = re.sub(r"\(index::([^\)]+)\)", r"(/lists/\1)", txt)
    txt = re.sub(r"\(([^\)]+)\.md\)", r"(/\1.html)", txt)
    txt = re.sub(r"\(([^\)]+)\.md#([^\)]+)\)", r"(/\1.html#\2)", txt)
    txt = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r"<a href='\2'>\1</a>", txt)
    return txt


def code_include(matches: typing.Match[str]) -> str:
    """Format code snippet.

    Args:
        matches: Code snippets

    Returns:
        HTML
    """
    out = "<p class='pcode'>"
    with open(os.path.join(settings.dir_path, matches[1])) as f:
        out += "<br />".join(line.replace(" ", "&nbsp;") for line in f)
    out += "</p>"
    return out


def author_info(matches: typing.Match[str]) -> str:
    """Format author info.

    Args:
        matches: author info

    Returns:
        HTML
    """
    authors, title, url = matches[1].split("|")
    authors = authors.split(";")
    out = "<div class='authors'>Written by "
    out += " ".join(" ".join(i.split(", ")[::-1]) for i in authors)
    out += (
        "</div>\n"
        "<a class='show_eg_link' href='javascript:show_author_cite_info()' id='showcitelink' "
        "style='display:block'>&darr; Cite this page &darr;</a>"
        "<div id='authorcite' style='display:none'>"
        "<a class='show_eg_link' href='javascript:hide_author_cite_info()' id='showcitelink' "
        "style='display:block'>&uarr; Hide citation info &uarr;</a>"
        "You can cite this page using the following BibTeX:\n\n"
        "```\n"
        "@misc{defelement,\n"
        f"       AUTHOR = {{{format_names(authors, 'bibtex')}}},\n"
        f"        TITLE = {{{{D}}ef{{E}}lement: {title}}},\n"
        "         YEAR = {{{{date:Y}}}},\n"
        f" HOWPUBLISHED = {{\\url{{https://defelement.com/{url}}}}},\n"
        "         NOTE = {[Online; accessed {{date:D-M-Y}}]}\n"
        "}\n"
        "```\n\n"
        "This will create a reference along the lines of:\n\n"
        "<ul class='citations'>"
        f"<li>{format_names(authors, 'citation')}. <i>DefElement: {title}</i>, {{{{date:Y}}}}, "
        f"<a href='https://defelement.com/{url}'>https://defelement.com/{url}</a> "
        "[Online; accessed: {{date:D-M-Y}}]</li>\n"
        "</ul></div>")
    return out


def plot_element(matches: typing.Match[str]) -> str:
    """Plot element.

    Args:
        matches: Element data

    Returns:
        HTML for plot of element
    """
    if "variant=" in matches[1]:
        a, b = matches[1].split(" variant=")
        e = symfem.create_element(a, matches[2], int(matches[3]), b)
    else:
        e = symfem.create_element(matches[1], matches[2], int(matches[3]))
    return ("<center>"
            f"{''.join([plotting.plot_function(e, i) for i in range(e.space_dim)])}"
            "</center>")


def plot_single_element(matches: typing.Match[str]) -> str:
    """Plot a single element.

    Args:
        matches: Element data

    Returns:
        HTML for plot of element
    """
    if "variant=" in matches[1]:
        a, b = matches[1].split(" variant=")
        e = symfem.create_element(a, matches[2], int(matches[3]), b)
    else:
        e = symfem.create_element(matches[1], matches[2], int(matches[3]))
    return f"<center>{plotting.plot_function(e, int(matches[4]))}</center>"


def plot_reference(matches: typing.Match[str]) -> str:
    """Plot references.

    Args:
        matches: Reference data

    Returns:
        HTML
    """
    e = symfem.create_reference(matches[1])
    return f"<center>{plotting.plot_reference(e)}</center>"


def plot_img(matches: typing.Match[str]) -> str:
    """Plot an image.

    Args:
        matches: Image info

    Returns:
        HTML for image
    """
    e = matches[1]
    return f"<center>{plotting.plot_img(e)}</center>"


def add_citation(matches: typing.Match[str]) -> str:
    """Add citation.

    Args:
        matches: Citation info

    Returns:
        HTML
    """
    global page_references
    from defelement.citations import markup_citation

    ref = {}
    for i in shlex.split(matches[1]):
        a, b = i.split("=")
        ref[a] = b
    page_references.append(markup_citation(ref))
    return f"<sup><a href='#ref{len(page_references)}'>[{len(page_references)}]</a></sup>"


def insert_dates(txt: str) -> str:
    """Insert dates.

    Args:
        txt: Text

    Returns:
        Text with dates inserted
    """
    now = datetime.now()
    txt = txt.replace("{{date:Y}}", now.strftime("%Y"))
    txt = txt.replace("{{date:D-M-Y}}", now.strftime("%d-%B-%Y"))
    txt = re.sub("{{symbols\\.([^}\\(]+)\\(([0-9]+)\\)}}",
                 lambda m: getattr(symbols, m[1])(int(m[2])), txt)
    txt = re.sub("{{symbols\\.([^}]+)}}", lambda m: getattr(symbols, m[1]), txt)

    return txt


def python_highlight(txt: str) -> str:
    """Apply syntax highlighting to Python snippet.

    Args:
        txt: Python snippet

    Returns:
        Snippet with syntax highlighting
    """
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


def bash_highlight(txt: str) -> str:
    """Apply syntax highlighting to Bash snippet.

    Args:
        txt: Bash snippet

    Returns:
        Snippet with syntax highlighting
    """
    txt = txt.replace(" ", "&nbsp;")
    txt = re.sub("(python3?(?:&nbsp;-m&nbsp;.+?)?&nbsp;)",
                 r"<span style='color:#FF8800'>\1</span>", txt)
    return "<br />".join(txt.split("\n"))
