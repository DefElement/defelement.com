import re
from symfem.symbolic import x
from datetime import datetime


def to_2d(c):
    if len(c) == 1:
        return (50 + c[0] * 100, 150)
    if len(c) == 2:
        return (50 + c[0] * 100, 150 - 100 * c[1])
    return (40 + c[0] * 100 + 50 * c[1], 150 - 100 * c[2] + 8 * c[0] - 20 * c[1])


def make_lattice(element, n, offset=False):
    if element.reference.name == "interval":
        if offset:
            return [((i + 0.5) / (n + 1), ) for i in range(n)]
        else:
            return [(i / (n - 1), ) for i in range(n)]
    elif element.reference.name == "triangle":
        if offset:
            return [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1)) for i in range(n) for j in range(n - i)]
        else:
            return [(i / (n - 1), j / (n - 1)) for i in range(n) for j in range(n - i)]
    elif element.reference.name == "tetrahedron":
        if offset:
            return [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1), (k + 0.5) / (n + 1)) for i in range(n) for j in range(n - i) for k in range(n - i - j)]
        else:
            return [(i / (n - 1), j / (n - 1), k / (n - 1)) for i in range(n) for j in range(n - i) for k in range(n - i - j)]
    elif element.reference.name == "quadrilateral":
        if offset:
            return [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1)) for i in range(n) for j in range(n)]
        else:
            return [(i / (n - 1), j / (n - 1)) for i in range(n) for j in range(n)]
    elif element.reference.name == "hexahedron":
        if offset:
            return [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1), (k + 0.5) / (n + 1)) for i in range(n) for j in range(n) for k in range(n)]
        else:
            return [(i / (n - 1), j / (n - 1), k / (n - 1)) for i in range(n) for j in range(n) for k in range(n)]
    raise ValueError("Unknown cell type.")


def subs(f, p):
    try:
        return [subs(i, p) for i in f]
    except:
        pass
    for i, j in zip(x, p):
        try:
            f = f.subs(i, j)
        except:
            pass
    return float(f)


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
    now = datetime.now()
    out = out.replace("{{date:Y}}", now.strftime("%Y"))
    out = out.replace("{{date:D-M-Y}}", now.strftime("%d-%B-%Y"))

    return out


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
        out += f" [DOI: <a href='https://doi.org/{r['doi']}'>{r['doi']}</a>]"
    return out


def markup_element(element):
    eg = ""

    if element.range_dim == 1:
        if element.reference.tdim not in [1, 2]:
            return ""

        reference = ""
        for edge in element.reference.edges:
            p0 = to_2d(element.reference.vertices[edge[0]] + (0, ))
            p1 = to_2d(element.reference.vertices[edge[1]] + (0, ))
            reference += f"<line x1='{p0[0]}' y1='{p0[1]}' x2='{p1[0]}' y2='{p1[1]}' stroke-width='4px' stroke-linecap='round' stroke='#AAAAAA' />"

        pairs = []
        if element.reference.tdim == 1:
            eval_points = make_lattice(element, 10, False)
            pairs = [(i, i+1) for i, j in enumerate(eval_points[:-1])]
        elif element.reference.tdim == 2:
            N = 6
            eval_points = make_lattice(element, N, False)
            if element.reference.name == "triangle":
                s = 0
                for j in range(N-1, 0, -1):
                    pairs += [(i, i+1) for i in range(s, s+j)]
                    s += j + 1
                for k in range(N + 1):
                    s = k
                    for i in range(N, k, -1):
                        if i != k + 1:
                            pairs += [(s, s + i)]
                        if k != 0:
                            pairs += [(s, s + i - 1)]
                        s += i
            if element.reference.name == "quadrilateral":
                for i in range(N):
                    for j in range(N):
                        node = i * N + j
                        if j != N - 1:
                            pairs += [(node, node + 1)]
                        if i != N - 1:
                            pairs += [(node, node + N)]
                            if j != 0:
                                pairs += [(node, node + N - 1)]

        max_l = 0
        for f in element.get_basis_functions():
            for p in eval_points:
                r1 = subs(f, p)
                max_l = max(max_l, r1)

        for f in element.get_basis_functions():
            eg += "<svg width='200' height='200'>\n"
            eg += reference
            for p, q in pairs:
                r1 = subs(f, eval_points[p])
                r2 = subs(f, eval_points[q])
                start = to_2d(eval_points[p] + (r1 / max_l, ))
                end = to_2d(eval_points[q] + (r2 / max_l, ))
                eg += f"<line x1='{start[0]}' y1='{start[1]}' x2='{end[0]}' y2='{end[1]}' stroke='#FF8800' stroke-width='2px' stroke-linecap='round' />"
            eg += "</svg>\n"

    elif element.range_dim == element.reference.tdim:
        eval_points = make_lattice(element, 6, True)

        reference = ""
        for edge in element.reference.edges:
            p0 = to_2d(element.reference.vertices[edge[0]])
            p1 = to_2d(element.reference.vertices[edge[1]])
            reference += f"<line x1='{p0[0]}' y1='{p0[1]}' x2='{p1[0]}' y2='{p1[1]}' stroke-width='4px' stroke-linecap='round' stroke='#AAAAAA' />"

        max_l = 0
        for f in element.get_basis_functions():
            for p in eval_points:
                res = subs(f, p)
                max_l = max(max_l, sum(i**2 for i in res) ** 0.5)


        for f in element.get_basis_functions():
            eg += "<svg width='200' height='200'>\n"
            eg += reference
            for p in eval_points:
                res = subs(f, p)
                start = to_2d(p)
                end = to_2d([i + j * 0.4 / max_l for i, j in zip(p, res)])
                a1 = [end[0] + 0.25 * (start[0] - end[0]) - 0.12 * (start[1] - end[1]),
                      end[1] + 0.25 * (start[1] - end[1]) + 0.12 * (start[0] - end[0])]
                a2 = [end[0] + 0.25 * (start[0] - end[0]) + 0.12 * (start[1] - end[1]),
                      end[1] + 0.25 * (start[1] - end[1]) - 0.12 * (start[0] - end[0])]
                wid = 4 * sum(i**2 for i in res) ** 0.5 / max_l
                eg += f"<line x1='{start[0]}' y1='{start[1]}' x2='{end[0]}' y2='{end[1]}' stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"
                eg += f"<line x1='{a1[0]}' y1='{a1[1]}' x2='{end[0]}' y2='{end[1]}' stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"
                eg += f"<line x1='{end[0]}' y1='{end[1]}' x2={a2[0]} y2={a2[1]} stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"

            eg += "</svg>\n"
    return eg
