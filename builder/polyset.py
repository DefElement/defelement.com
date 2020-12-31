import re
import yaml
import os

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/polysets")) as f:
    poly_sets = yaml.load(f, Loader=yaml.FullLoader)

named = {}


def make_name(i):
    return f"\\mathcal{{Z}}^{{({i})}}"


def make_poly_set(p):
    global named
    if "&&" in p:
        return " \\oplus ".join([make_poly_set(i.strip()) for i in p.split("&&")])
    p = p.strip()
    if re.match(r"^\[([^\]]+)\]\[(.+)\]$", p):
        order = re.match(r"^\[([^\]]+)\]\[(.+)\]$", p)[1]
        the_set = re.match(r"^\[([^\]]+)\]\[(.+)\]$", p)[2]
        if the_set not in named:
            named[the_set] = make_name(len(named))
        return f"{named[the_set]}_{{{order}}}"
    for i, (j, k) in poly_sets.items():
        if re.match(rf"^{i}\[([^\]]+)\]$", p):
            order = re.match(rf"^{i}\[([^\]]+)\]$", p)[1]
            return f"{j}_{{{order}}}"
        if re.match(rf"^{i}\[([^\]]+)\]\^d$", p):
            order = re.match(rf"^{i}\[([^\]]+)\]\^d$", p)[1]
            return f"{j}_{{{order}}}^d"
        if re.match(rf"^{i}\[([^\]]+)\]\(([^\)]+)\)$", p):
            order = re.match(rf"^{i}\[([^\]]+)\]\(([^\)]+)\)$", p)[1]
            dim = re.match(rf"^{i}\[([^\]]+)\]\(([^\)]+)\)$", p)[2]
            return f"{j}_{{{order}}}^d(\\mathbb{{R}}^{{{dim}}})"
    raise ValueError(f"Unknown polynomial set: {p}")


def make_extra_info(p):
    done = []
    out = []
    for a in p.split("&&"):
        a = a.strip()
        if re.match(r"^\[([^\]]+)\]\[(.+)\]$", a):
            the_set = re.match(r"^\[([^\]]+)\]\[(.+)\]$", a)[2]
            out.append(f"\\({named[the_set]}_k={insert_terms(the_set)}\\)")
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
            if re.match(rf"^{i}\[([^\]]+)\](?:\^d)?$", a):
                if i not in done:
                    out.append(f"\\({j}_k={k}\\)")
                    done.append(i)
                break
        else:
            raise ValueError(f"Unknown polynomial set: {a}")
    return "<br /><br />".join(out)


def insert_terms(the_set):
    the_set = the_set.replace("{{x}}", "\\mathbf{x}")
    for i, (j, k) in poly_sets.items():
        the_set = re.sub(rf"{{{{{i}\[([^\]]+)\]\^d}}}}", rf"{escape(j)}_{{\1}}^d", the_set)
        the_set = re.sub(rf"{{{{{i}\[([^\]]+)\]}}}}", rf"{escape(j)}_{{\1}}", the_set)
        the_set = re.sub(rf"{{{{{i}\[([^\]]+)\]\(([^\)]+)\)}}}}",
                         rf"{escape(j)}_{{\1}}(\\mathbb{{R}}^{{\2}})", the_set)

    return the_set


def escape(i):
    return i.replace("\\", "\\\\")
