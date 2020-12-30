import symbols
import sympy
from symfem import functionals
from symfem.symbolic import x


def to_2d(c, width=200, height=200):
    if height > 100:
        hst = 50 + height / 2
    else:
        hst = height / 2
    if len(c) == 1:
        return ((width - 100) / 2 + c[0] * 100, hst)
    if len(c) == 2:
        return ((width - 100) / 2 + c[0] * 100, hst - 100 * c[1])
    return ((width - 120) / 2 + c[0] * 100 + 50 * c[1], hst - 100 * c[2] + 8 * c[0] - 20 * c[1])


def make_lattice(element, n, offset=False):
    if element.reference.name == "interval":
        if offset:
            return [((i + 0.5) / (n + 1), ) for i in range(n)]
        else:
            return [(i / (n - 1), ) for i in range(n)]
    elif element.reference.name == "triangle":
        if offset:
            return [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1))
                    for i in range(n) for j in range(n - i)]
        else:
            return [(i / (n - 1), j / (n - 1)) for i in range(n) for j in range(n - i)]
    elif element.reference.name == "tetrahedron":
        if offset:
            return [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1), (k + 0.5) / (n + 1))
                    for i in range(n) for j in range(n - i) for k in range(n - i - j)]
        else:
            return [(i / (n - 1), j / (n - 1), k / (n - 1))
                    for i in range(n) for j in range(n - i) for k in range(n - i - j)]
    elif element.reference.name == "quadrilateral":
        if offset:
            return [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1)) for i in range(n) for j in range(n)]
        else:
            return [(i / (n - 1), j / (n - 1)) for i in range(n) for j in range(n)]
    elif element.reference.name == "hexahedron":
        if offset:
            return [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1), (k + 0.5) / (n + 1))
                    for i in range(n) for j in range(n) for k in range(n)]
        else:
            return [(i / (n - 1), j / (n - 1), k / (n - 1))
                    for i in range(n) for j in range(n) for k in range(n)]
    raise ValueError("Unknown cell type.")


def subs(f, p):
    try:
        return [subs(i, p) for i in f]
    except:  # noqa: E722
        pass
    for i, j in zip(x, p):
        try:
            f = f.subs(i, j)
        except:  # noqa: E722
            pass
    return float(f)


def svg_reference(ref):
    if ref.name == "interval":
        w = 130
        h = 30
    elif ref.tdim == 3:
        w = 146
        h = 146
    else:
        w = 130
        h = 130
    out = f"<svg width='{w}' height='{h}'>"
    if ref.tdim == 3:
        fg = ""

        for edge in ref.edges:
            v0 = ref.vertices[edge[0]]
            v1 = ref.vertices[edge[1]]
            p0 = to_2d(v0, w, h)
            p1 = to_2d(v1, w, h)
            if v0[1] < 0.1 and v1[1] < 0.1:
                fg += f"<line x1='{p0[0]}' y1='{p0[1]}' x2='{p1[0]}' y2='{p1[1]}'"
                fg += " stroke-width='4px' stroke-linecap='round' stroke='#000000' />"
            else:
                out += f"<line x1='{p0[0]}' y1='{p0[1]}' x2='{p1[0]}' y2='{p1[1]}'"
                out += " stroke-width='4px' stroke-linecap='round' stroke='#000000' />"

        for i, v in enumerate(ref.vertices):
            if v[1] < 0.1:
                fg += dof_arrow(v, None, i, "#FF8800", width=w, height=h)
            else:
                out += dof_arrow(v, None, i, "#FF8800", width=w, height=h)

        for i, e in enumerate(ref.edges):
            c = tuple(sum(j) / len(j) for j in zip(*[ref.vertices[k] for k in e]))
            if c[1] < 0.1:
                fg += dof_arrow(c, None, i, "#44AAFF", width=w, height=h)
            else:
                out += dof_arrow(c, None, i, "#44AAFF", width=w, height=h)

        for i, e in enumerate(ref.faces):
            c = tuple(sum(j) / len(j) for j in zip(*[ref.vertices[k] for k in e]))
            if c[1] < 0.1:
                fg += dof_arrow(c, None, i, "#55FF00", width=w, height=h)
            else:
                out += dof_arrow(c, None, i, "#55FF00", width=w, height=h)

        for i, e in enumerate(ref.volumes):
            c = tuple(sum(j) / len(j) for j in zip(*[ref.vertices[k] for k in e]))
            if c[1] < 0.1:
                fg += dof_arrow(c, None, i, "#DD2299", width=w, height=h)
            else:
                out += dof_arrow(c, None, i, "#DD2299", width=w, height=h)
        out += fg
    else:
        for edge in ref.edges:
            p0 = to_2d(ref.vertices[edge[0]], w, h)
            p1 = to_2d(ref.vertices[edge[1]], w, h)
            out += f"<line x1='{p0[0]}' y1='{p0[1]}' x2='{p1[0]}' y2='{p1[1]}'"
            out += " stroke-width='4px' stroke-linecap='round' stroke='#000000' />"

        for i, v in enumerate(ref.vertices):
            out += dof_arrow(v, None, i, "#FF8800", width=w, height=h)

        for i, e in enumerate(ref.edges):
            c = tuple(sum(j) / len(j) for j in zip(*[ref.vertices[k] for k in e]))
            out += dof_arrow(c, None, i, "#44AAFF", width=w, height=h)

        for i, e in enumerate(ref.faces):
            c = tuple(sum(j) / len(j) for j in zip(*[ref.vertices[k] for k in e]))
            out += dof_arrow(c, None, i, "#55FF00", width=w, height=h)

        for i, e in enumerate(ref.volumes):
            c = tuple(sum(j) / len(j) for j in zip(*[ref.vertices[k] for k in e]))
            out += dof_arrow(c, None, i, "#DD2299", width=w, height=h)
    out += "</svg>"

    return out


def to_tex(f, tfrac=False):
    try:
        return "\\left(\\begin{array}{c}" + "\\\\".join(
            [to_tex(i, tfrac) for i in f]) + "\\end{array}\\right)"
    except:  # noqa: E722
        if tfrac:
            return sympy.latex(f).replace("\\frac", "\\tfrac")
        else:
            return sympy.latex(f)


def get_entity_number(element, dof):
    if dof.entity_dim() == 1:
        entities = element.reference.edges
    elif dof.entity_dim() == 2:
        entities = element.reference.faces
    elif dof.entity_dim() == 2:
        entities = element.reference.volumes
    return str(entities.index(
        tuple(element.reference.vertices.index(i)
              for i in dof.reference.vertices)))


def describe_dof(element, d):
    if isinstance(d, functionals.PointEvaluation):
        return "v\\mapsto v(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
    elif isinstance(d, functionals.DotPointEvaluation):
        desc = "\\mathbf{v}\\mapsto"
        desc += "\\mathbf{v}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        desc += "\\cdot\\left(\\begin{array}{c}"
        desc += "\\\\".join([to_tex(i) for i in d.dof_direction()])
        desc += "\\end{array}\\right)"
        return desc
    elif isinstance(d, functionals.TangentIntegralMoment):
        entity = symbols.entity(d.entity_dim())
        entity_n = get_entity_number(element, d)
        desc = "\\mathbf{v}\\mapsto"
        desc += f"\\displaystyle\\int_{{{entity}_{{{entity_n}}}}}"
        desc += "\\mathbf{v}\\cdot"
        if d.f != 1:
            desc += "(" + to_tex(d.f) + ")"
        desc += "\\hat{\\mathbf{t}}" + f"_{{{entity_n}}}"
        return desc
    elif isinstance(d, functionals.NormalIntegralMoment):
        entity = symbols.entity(d.entity_dim())
        entity_n = get_entity_number(element, d)
        desc = "\\mathbf{v}\\mapsto"
        desc += f"\\displaystyle\\int_{{{entity}_{{{entity_n}}}}}"
        desc += "\\mathbf{v}\\cdot"
        if d.f != 1:
            desc += "(" + to_tex(d.f, True) + ")"
        desc += "\\hat{\\mathbf{n}}" + f"_{{{entity_n}}}"
        return desc
    elif isinstance(d, functionals.IntegralMoment):
        if d.entity_dim() == element.reference.tdim:
            entity = symbols.reference
        else:
            entity = f"{symbols.entity(d.entity_dim())}_{{{get_entity_number(element, d)}}}"
        try:
            d.f[0]
            desc = "\\mathbf{v}\\mapsto"
            desc += f"\\displaystyle\\int_{{{entity}}}"
            desc += "\\mathbf{v}\\cdot"
            desc += "\\left(\\begin{array}{c}"
            desc += "\\\\".join([to_tex(i) for i in d.f])
            desc += "\\end{array}\\right)"
        except:  # noqa: E722
            desc = "v\\mapsto"
            desc += f"\\displaystyle\\int_{{{entity}}}"
            if d.f != 1:
                desc += "(" + to_tex(d.f) + ")"
            desc += "v"
        return desc
    else:
        raise ValueError(f"Unknown functional: {d.__class__}")


def markup_element(element, images_only=False):
    eg = ""
    if not images_only:
        eg += "<ul>\n"
        # Reference
        eg += f"<li>\\({symbols.reference}\\) is the reference {element.reference.name}</li>\n"
        eg += "<center>" + svg_reference(element.reference) + "</center>\n"
        # Polynomial set
        eg += f"<li>\\({symbols.polyset}\\) is spanned by: "
        eg += ", ".join(["\\(" + to_tex(i) + "\\)" for i in element.basis])
        eg += "</li>\n"
        # Dual basis
        eg += f"<li>\\({symbols.dual_basis}=\\{{{symbols.functional}_0,"
        eg += f"...,{symbols.functional}_{{{len(element.dofs) - 1}}}\\}}\\)</li>\n"

        # Basis functions
        eg += "<li>Functionals and basis functions:</li>"
        eg += "</ul>"

    if element.range_dim == 1:
        if element.reference.tdim not in [1, 2]:
            return ""

        reference = ""
        for edge in element.reference.edges:
            p0 = to_2d(element.reference.vertices[edge[0]] + (0, ))
            p1 = to_2d(element.reference.vertices[edge[1]] + (0, ))
            reference += f"<line x1='{p0[0]}' y1='{p0[1]}' x2='{p1[0]}' y2='{p1[1]}'"
            reference += " stroke-width='4px' stroke-linecap='round' stroke='#AAAAAA' />"

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

        for dof_i, (dof, func) in enumerate(zip(element.dofs, element.get_basis_functions())):
            if not images_only:
                eg += "<div class='basisf'>"
                eg += "<div style='display:inline-block'>"
            eg += "<svg width='200' height='200' style='vertical-align:middle'>\n"
            eg += reference
            assert dof.dof_direction() is None
            eg += dof_arrow(dof.dof_point() + (0, ), None, dof_i, "#DD2299")
            for p, q in pairs:
                r1 = subs(func, eval_points[p])
                r2 = subs(func, eval_points[q])
                start = to_2d(eval_points[p] + (r1 / max_l, ))
                end = to_2d(eval_points[q] + (r2 / max_l, ))
                eg += f"<line x1='{start[0]}' y1='{start[1]}' x2='{end[0]}' y2='{end[1]}'"
                eg += " stroke='#FF8800' stroke-width='2px' stroke-linecap='round' />"
            eg += "</svg>\n"
            if not images_only:
                eg += "</div><div style='display:inline-block'>"
                eg += f"\\(\\displaystyle {symbols.functional}_{{{dof_i}}}:" + describe_dof(element, dof) + "\\)<br /><br />"
                eg += f"\\(\\displaystyle {symbols.basis_function}_{{{dof_i}}} = " + to_tex(func) + "\\)"
                eg += "</div></div>\n"

    elif element.range_dim == element.reference.tdim:
        eval_points = make_lattice(element, 6, True)

        reference = ""
        for edge in element.reference.edges:
            p0 = to_2d(element.reference.vertices[edge[0]])
            p1 = to_2d(element.reference.vertices[edge[1]])
            reference += f"<line x1='{p0[0]}' y1='{p0[1]}' x2='{p1[0]}' y2='{p1[1]}'"
            reference += " stroke-width='4px' stroke-linecap='round' stroke='#AAAAAA' />"

        max_l = 0
        for f in element.get_basis_functions():
            for p in eval_points:
                res = subs(f, p)
                max_l = max(max_l, sum(i**2 for i in res) ** 0.5)

        for dof_i, (dof, func) in enumerate(zip(element.dofs, element.get_basis_functions())):
            if not images_only:
                eg += "<div class='basisf'>"
                eg += "<div style='display:inline-block'>"
            eg += "<svg width='200' height='200' style='vertical-align:middle'>\n"
            eg += reference
            for p in eval_points:
                res = subs(func, p)
                start = to_2d(p)
                end = to_2d([i + j * 0.4 / max_l for i, j in zip(p, res)])
                a1 = [end[0] + 0.25 * (start[0] - end[0]) - 0.12 * (start[1] - end[1]),
                      end[1] + 0.25 * (start[1] - end[1]) + 0.12 * (start[0] - end[0])]
                a2 = [end[0] + 0.25 * (start[0] - end[0]) + 0.12 * (start[1] - end[1]),
                      end[1] + 0.25 * (start[1] - end[1]) - 0.12 * (start[0] - end[0])]
                wid = 4 * sum(i**2 for i in res) ** 0.5 / max_l
                eg += f"<line x1='{start[0]}' y1='{start[1]}' x2='{end[0]}' y2='{end[1]}'"
                eg += f" stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"
                eg += f"<line x1='{a1[0]}' y1='{a1[1]}' x2='{end[0]}' y2='{end[1]}'"
                eg += f" stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"
                eg += f"<line x1='{end[0]}' y1='{end[1]}' x2={a2[0]} y2={a2[1]}"
                eg += f" stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"

            eg += dof_arrow(dof.dof_point(), dof.dof_direction(), dof_i, "#DD2299")

            eg += "</svg>\n"
            if not images_only:
                eg += "</div><div style='display:inline-block'>"
                eg += f"\\[{symbols.functional}_{{{dof_i}}}:" + describe_dof(element, dof) + "\\]"
                eg += f"\\[{symbols.basis_function}_{{{dof_i}}} = " + to_tex(func) + "\\]"
                eg += "</div></div>"
    return eg


def dof_arrow(point, dir, n, color="#000000", width=200, height=200):
    out = ""
    start = to_2d(tuple(float(i) for i in point), width=width, height=height)
    if dir is not None:
        norma = sum(i**2 for i in dir) ** 0.5
        dir = tuple(i / norma for i in dir)
        end = to_2d(tuple(float(i + j/4) for i, j in zip(point, dir)), width=width, height=height)
        a1 = [end[0] + 0.25 * (start[0] - end[0]) - 0.12 * (start[1] - end[1]),
              end[1] + 0.25 * (start[1] - end[1]) + 0.12 * (start[0] - end[0])]
        a2 = [end[0] + 0.25 * (start[0] - end[0]) + 0.12 * (start[1] - end[1]),
              end[1] + 0.25 * (start[1] - end[1]) - 0.12 * (start[0] - end[0])]
        out += f"<line x1='{start[0]}' y1='{start[1]}' x2='{end[0]}' y2='{end[1]}'"
        out += f" stroke='{color}' stroke-width='2px' stroke-linecap='round' />"
        out += f"<line x1='{a1[0]}' y1='{a1[1]}' x2='{end[0]}' y2='{end[1]}'"
        out += f" stroke='{color}' stroke-width='2px' stroke-linecap='round' />"
        out += f"<line x1='{end[0]}' y1='{end[1]}' x2={a2[0]} y2={a2[1]}"
        out += f" stroke='{color}' stroke-width='2px' stroke-linecap='round' />"

    out += f"<circle cx='{start[0]}' cy='{start[1]}' r='10px' fill='white'"
    out += f" stroke='{color}' stroke-width='2px' />"
    cl = "dofnum"
    if n >= 10:
        cl += " largen"
    out += f"<text x='{start[0]}' y='{start[1]}' text-anchor='middle' dominant-baseline='middle'"
    out += f" fill='{color}' class='{cl}'>{n}</text>"

    return out
