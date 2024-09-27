"""Polynomial sets."""

import os
import re
import typing

import yaml

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/polysets")) as f:
    poly_sets = yaml.load(f, Loader=yaml.FullLoader)

named: typing.Dict[str, typing.Tuple[str, str, typing.Dict[str, str]]] = {}
defs: typing.Dict[str, str] = {}


def make_name(i: int) -> str:
    """Make a polyset name.

    Args:
        i: Polyset id

    Returns:
        Polyset name
    """
    return f"\\mathcal{{Z}}^{{({i})}}"


def replace_def(matches: typing.Match[str]) -> str:
    """Replace def.

    Args:
        matches: TODO

    Returns:
        TODO
    """
    global defs
    defs[matches[1]] = matches[2]
    return ""


def replace_defmath(matches: typing.Match[str]) -> str:
    """Replace def.

    Args:
        matches: TODO

    Returns:
        TODO
    """
    global defs
    defs[matches[1]] = f"\\({matches[2]}\\)"
    return ""


def _get_match(
    regex: str, string: str, index: int
) -> str:
    """Get a regular expression match.

    Args:
        regex: Regular expression
        string: Search string
        index: Index

    Return: Match
    """
    m = re.match(regex, string)
    assert m is not None
    return m[index]


def make_poly_set(p: str) -> str:
    """Make a polynomial set.

    Args:
        p: Polyset data

    Returns:
        Formatted polynomial set
    """
    global named
    global defs
    if "&&" in p:
        return " \\oplus ".join([make_poly_set(i.strip()) for i in p.split("&&")])
    p = p.strip()
    if re.match(r"^\<([^\]]+)\>\[(.+)\]$", p):
        degree = _get_match(r"^\<([^\]]+)\>\[(.+)\]$", p, 1)
        the_set = _get_match(r"^\<([^\]]+)\>\[(.+)\]$", p, 2)
        defs = {}
        the_set_out = re.sub(r"\@def\@([^\@]+)\@([^\@]+)\@", replace_def, the_set)
        the_set_out = re.sub(r"\@defmath\@([^\@]+)\@([^\@]+)\@", replace_defmath, the_set_out)
        if the_set not in named:
            named[the_set] = (make_name(len(named)), the_set_out, defs)
        return f"{named[the_set][0]}_{{{degree}}}"
    if re.match(r"^\<([^\]]+)\>\[(.+)\]\^d$", p):
        degree = _get_match(r"^\<([^\]]+)\>\[(.+)\]\^d$", p, 1)
        the_set = _get_match(r"^\<([^\]]+)\>\[(.+)\]\^d$", p, 2)
        defs = {}
        the_set_out = re.sub(r"\@def\@([^\@]+)\@([^\@]+)\@", replace_def, the_set)
        the_set_out = re.sub(r"\@defmath\@([^\@]+)\@([^\@]+)\@", replace_defmath, the_set_out)
        if the_set not in named:
            named[the_set] = (make_name(len(named)), the_set_out, defs)
        return f"\\left({named[the_set][0]}_{{{degree}}}\\right)^d"
    for i, (j, k) in poly_sets.items():
        if re.match(rf"^{i}\[([^\]]+)\]$", p):
            degree = _get_match(rf"^{i}\[([^\]]+)\]$", p, 1)
            return f"{j}_{{{degree}}}"
        if re.match(rf"^{i}\[([^\]]+)\]\^dd$", p):
            degree = _get_match(rf"^{i}\[([^\]]+)\]\^dd$", p, 1)
            return f"{j}_{{{degree}}}^{{d\\times d}}"
        if re.match(rf"^{i}\[([^\]]+)\]\^d$", p):
            degree = _get_match(rf"^{i}\[([^\]]+)\]\^d$", p, 1)
            return f"{j}_{{{degree}}}^d"
        if re.match(rf"^{i}\[([^\]]+)\]\(([^\)]+)\)$", p):
            degree = _get_match(rf"^{i}\[([^\]]+)\]\(([^\)]+)\)$", p, 1)
            dim = _get_match(rf"^{i}\[([^\]]+)\]\(([^\)]+)\)$", p, 2)
            return f"{j}_{{{degree}}}^d(\\mathbb{{R}}^{{{dim}}})"
    raise ValueError(f"Unknown polynomial set: {p}")


def make_extra_info(p: str) -> str:
    """Make extra info.

    Args:
        p: Polyset data

    Returns:
        Extra info
    """
    done = []
    out = []
    for a in p.split("&&"):
        a = a.strip()
        if re.match(r"^\<([^\]]+)\>\[(.+)\](?:\^d)?$", a):
            the_set = _get_match(r"^\<([^\]]+)\>\[(.+)\](?:\^d)?$", a, 2)
            if named[the_set] not in done:
                def_txt = ""
                if len(named[the_set][2]) > 0:
                    def_txt = "<br />where<ul>"
                    def_txt += "\n".join([f"<li>\\({i}\\) is {j}</li>"
                                          for i, j in named[the_set][2].items()])
                    def_txt += "</ul>"
                out.append(
                    f"\\({named[the_set][0]}_k={insert_terms(named[the_set][1])}\\){def_txt}")
                done.append(named[the_set])
            for i, (j, k) in poly_sets.items():
                if f"{{{{{i}[" in a and i not in done:
                    out.append(f"\\({j}_k={k}\\)")
                    done.append(i)
            continue
        for i, (j, k) in poly_sets.items():
            if re.match(rf"^{i}\[([^\]]+)\]\(([^\)]+)\)$", p):
                if i + "(d)" not in done:
                    out.append(f"\\({j}_k(\\mathbb{{R}}^d)={k}\\)")
                    done.append(i)
                break
            if re.match(rf"^{i}\[([^\]]+)\](?:\^d+)?$", a):
                if i not in done:
                    out.append(f"\\({j}_k={k}\\)")
                    done.append(i)
                break
        else:
            raise ValueError(f"Unknown polynomial set: {a}")
    return "<br /><br />".join(out)


def insert_terms(the_set: str) -> str:
    """Insert terms into a polyset definition.

    Args:
        the_set: Polynomial set

    Returns:
        Formatted polynomial set
    """
    the_set = the_set.replace("{{x}}", "\\boldsymbol{x}")
    for i, (j, k) in poly_sets.items():
        the_set = re.sub(rf"{{{{{i}\[([^\]]+)\]\^dd}}}}", rf"{escape(j)}_{{\1}}^{{d\\times d}}",
                         the_set)
        the_set = re.sub(rf"{{{{{i}\[([^\]]+)\]\^d}}}}", rf"{escape(j)}_{{\1}}^d", the_set)
        the_set = re.sub(rf"{{{{{i}\[([^\]]+)\]}}}}", rf"{escape(j)}_{{\1}}", the_set)
        the_set = re.sub(rf"{{{{{i}\[([^\]]+)\]\(([^\)]+)\)}}}}",
                         rf"{escape(j)}_{{\1}}(\\mathbb{{R}}^{{\2}})", the_set)

    return the_set


def escape(i: str) -> str:
    """Escape a string.

    Args:
        i: The string

    Returns:
        Escaped string
    """
    return i.replace("\\", "\\\\")
