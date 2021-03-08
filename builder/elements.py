import symbols
import sympy
from symfem import create_element
from symfem.core import functionals
from symfem.core.symbolic import x, PiecewiseFunction
from symfem.core.calculus import grad
from symfem.core.vectors import vdot, vsub


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
            return [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1))
                    for i in range(n + 1) for j in range(n + 1)]
        else:
            return [(i / (n - 1), j / (n - 1)) for i in range(n) for j in range(n)]
    elif element.reference.name == "hexahedron":
        if offset:
            return [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1), (k + 0.5) / (n + 1))
                    for i in range(n + 1) for j in range(n + 1) for k in range(n + 1)]
        else:
            return [(i / (n - 1), j / (n - 1), k / (n - 1))
                    for i in range(n) for j in range(n) for k in range(n)]
    raise ValueError("Unknown cell type.")


def subs(f, p):
    if isinstance(f, (tuple, list)):
        return [subs(i, p) for i in f]
    if isinstance(f, PiecewiseFunction):
        return subs(f.get_piece(p), p)
    for i, j in zip(x, p):
        try:
            f = f.subs(i, j)
        except:  # noqa: E722
            pass
    return float(f)


def svg_reference(ref):
    if ref.name == "dual polygon":
        return svg_dual_reference(ref)
    elif ref.name == "interval":
        w = 130
        h = 30
    elif ref.name == "hexahedron":
        w = 210
        h = 165
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


def svg_dual_reference(ref):
    assert ref.name == "dual polygon"
    assert ref.tdim == 2

    out = "<svg width='260' height='260'>"

    for v in ref.vertices:
        p0 = [float(130 + 110 * i) for i in ref.origin]
        p1 = [float(130 + 110 * i) for i in v]
        out += f"<line x1='{p0[0]}' y1='{p0[1]}' x2='{p1[0]}' y2='{p1[1]}'"
        out += " stroke-width='2px' stroke-linecap='round' stroke='#AAAAAA'"
        out += " stroke-dasharray='3, 5' />"
    for edge in ref.edges:
        p0 = [float(130 + 110 * i) for i in ref.vertices[edge[0]]]
        p1 = [float(130 + 110 * i) for i in ref.vertices[edge[1]]]
        out += f"<line x1='{p0[0]}' y1='{p0[1]}' x2='{p1[0]}' y2='{p1[1]}'"
        out += " stroke-width='4px' stroke-linecap='round' stroke='#000000' />"

    for i, v in enumerate(ref.vertices):
        out += dof_arrow([float(130 + 110 * i) for i in v], None, i, "#FF8800", map_to_2d=False)

    for i, e in enumerate(ref.edges):
        c = tuple(sum(j) / len(j) for j in zip(*[ref.vertices[k] for k in e]))
        out += dof_arrow([float(130 + 110 * i) for i in c], None, i, "#44AAFF", map_to_2d=False)

    for i, e in enumerate(ref.faces):
        c = tuple(sum(j) / len(j) for j in zip(*[ref.vertices[k] for k in e]))
        out += dof_arrow([float(130 + 110 * i) for i in c], None, i, "#55FF00", map_to_2d=False)

    for i, e in enumerate(ref.volumes):
        c = tuple(sum(j) / len(j) for j in zip(*[ref.vertices[k] for k in e]))
        out += dof_arrow([float(130 + 110 * i) for i in c], None, i, "#DD2299", map_to_2d=False)
    out += "</svg>"

    return out


def to_tex(f, tfrac=False):
    if isinstance(f, (list, tuple)):
        return "\\left(\\begin{array}{c}" + "\\\\".join(
            ["\\displaystyle " + to_tex(i) for i in f]) + "\\end{array}\\right)"
    if isinstance(f, PiecewiseFunction):
        out = "\\begin{cases}\n"
        joiner = ""
        for points, func in f.pieces:
            out += joiner
            joiner = "\\\\"
            out += to_tex(func, True)
            out += f"&\\text{{in }}\\operatorname{{Triangle}}({points})"
        out += "\\end{cases}"
        return out
    out = sympy.latex(sympy.simplify(sympy.expand(f)))
    out = out.replace("\\left[", "\\left(")
    out = out.replace("\\right]", "\\right)")
    if tfrac:
        return out.replace("\\frac", "\\tfrac")
    else:
        return out


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
        desc = "\\boldsymbol{v}\\mapsto"
        desc += "\\boldsymbol{v}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        desc += "\\cdot\\left(\\begin{array}{c}"
        desc += "\\\\".join([to_tex(i) for i in d.dof_direction()])
        desc += "\\end{array}\\right)"
        return desc
    elif isinstance(d, functionals.PointNormalDerivativeEvaluation):
        desc = "v\\mapsto"
        desc += "\\nabla{v}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        entity_n = get_entity_number(element, d)
        desc += "\\cdot\\hat{\\boldsymbol{n}}" + f"_{{{entity_n}}}"
        return desc
    elif isinstance(d, functionals.PointDirectionalDerivativeEvaluation):
        if element.reference.tdim == 1:
            desc = "v\\mapsto "
            desc += "v'(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
            return desc
        desc = "v\\mapsto"
        desc += "\\nabla{v}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        desc += "\\cdot\\left(\\begin{array}{c}"
        desc += "\\\\".join([to_tex(i) for i in d.dof_direction()])
        desc += "\\end{array}\\right)"
        return desc
    elif isinstance(d, functionals.DerivativePointEvaluation):
        if element.reference.tdim == 1:
            desc = "v\\mapsto "
            desc += "v'(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
            return desc
        desc = "v\\mapsto"
        desc += f"\\frac{{\\partial^{{{sum(d.derivative)}}}}}{{"
        for v, i in zip("xyz", d.derivative):
            if i > 0:
                desc += f"\\partial {v}"
                if i > 1:
                    desc += f"^{{{i}}}"
        desc += "}"
        desc += "\\nabla{v}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        return desc
    elif isinstance(d, functionals.PointComponentSecondDerivativeEvaluation):
        desc = "v\\mapsto"
        desc += "\\frac{\\partial^2v}{"
        for c in d.component:
            desc += "\\partial " + "xyz"[c]
        desc += "}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        return desc
    elif isinstance(d, functionals.TangentIntegralMoment):
        entity = symbols.entity(d.entity_dim())
        entity_n = get_entity_number(element, d)
        desc = "\\boldsymbol{v}\\mapsto"
        desc += f"\\displaystyle\\int_{{{entity}_{{{entity_n}}}}}"
        desc += "\\boldsymbol{v}\\cdot"
        if d.f != 1:
            desc += "(" + to_tex(d.f) + ")"
        desc += "\\hat{\\boldsymbol{t}}" + f"_{{{entity_n}}}"
        return desc
    elif isinstance(d, functionals.NormalIntegralMoment):
        entity = symbols.entity(d.entity_dim())
        entity_n = get_entity_number(element, d)
        desc = "\\boldsymbol{v}\\mapsto"
        desc += f"\\displaystyle\\int_{{{entity}_{{{entity_n}}}}}"
        desc += "\\boldsymbol{v}\\cdot"
        if d.f != 1:
            desc += "(" + to_tex(d.f, True) + ")"
        desc += "\\hat{\\boldsymbol{n}}" + f"_{{{entity_n}}}"
        return desc
    elif isinstance(d, functionals.NormalInnerProductIntegralMoment):
        entity = symbols.entity(d.entity_dim())
        entity_n = get_entity_number(element, d)
        desc = "\\mathbf{V}\\mapsto"
        desc += f"\\displaystyle\\int_{{{entity}_{{{entity_n}}}}}"
        if d.f != 1:
            desc += "(" + to_tex(d.f, True) + ")"
        desc += f"|{{{entity}_{{{entity_n}}}}}|"
        desc += "\\hat{\\boldsymbol{n}}^t" + f"_{{{entity_n}}}"
        desc += "\\mathbf{V}"
        desc += "\\hat{\\boldsymbol{n}}" + f"_{{{entity_n}}}"
        return desc
    elif isinstance(d, functionals.IntegralAgainst):
        entity = symbols.entity(d.entity_dim())
        entity_n = get_entity_number(element, d)
        desc = "\\mathbf{V}\\mapsto"
        desc += f"\\displaystyle\\int_{{{entity}_{{{entity_n}}}}}"
        if d.f != 1:
            desc += "(" + to_tex(d.f, True) + ")"
        desc += "v"
        return desc
    elif isinstance(d, functionals.IntegralMoment):
        if d.entity_dim() == element.reference.tdim:
            entity = symbols.reference
        else:
            entity = f"{symbols.entity(d.entity_dim())}_{{{get_entity_number(element, d)}}}"
        try:
            d.f[0]
            if len(d.f) == element.reference.tdim:
                desc = "\\boldsymbol{v}\\mapsto"
                desc += f"\\displaystyle\\int_{{{entity}}}"
                desc += "\\boldsymbol{v}\\cdot"
                desc += "\\left(\\begin{array}{c}"
                desc += "\\\\".join([to_tex(i) for i in d.f])
                desc += "\\end{array}\\right)"
            else:
                assert len(d.f) == element.reference.tdim ** 2
                desc = "\\mathbf{V}\\mapsto"
                desc += f"\\displaystyle\\int_{{{entity}}}"
                desc += "\\mathbf{V}:"
                desc += "\\left(\\begin{array}{" + "c" * element.reference.tdim + "}"
                desc += "\\\\".join(["&".join(
                    [to_tex(d.f[i]) for i in range(element.reference.tdim * row,
                                                   element.reference.tdim * (row + 1))]
                ) for row in range(element.reference.tdim)])
                desc += "\\end{array}\\right)"
        except:  # noqa: E722
            desc = "v\\mapsto"
            desc += f"\\displaystyle\\int_{{{entity}}}"
            if d.f != 1:
                desc += "(" + to_tex(d.f) + ")"
            desc += "v"
        return desc
    elif isinstance(d, functionals.PointInnerProduct):
        desc = "\\mathbf{V}\\mapsto"
        desc += "\\left(\\begin{array}{c}"
        desc += "\\\\".join([to_tex(i) for i in d.lvec])
        desc += "\\end{array}\\right)^t"
        desc += "\\mathbf{V}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        desc += "\\left(\\begin{array}{c}"
        desc += "\\\\".join([to_tex(i) for i in d.rvec])
        desc += "\\end{array}\\right)"
        return desc
    else:
        raise ValueError(f"Unknown functional: {d.__class__}")


def draw_reference(reference, dof_entity=(-1, -1), add=tuple()):
    out = ""

    if dof_entity[0] >= 2:
        if dof_entity[0] == 2:
            faces = [dof_entity[1]]
        else:
            faces = [i for i, _ in enumerate(reference.faces)]
        for f in faces:
            vertices = [to_2d(reference.vertices[i] + add) for i in reference.faces[f]]
            if len(vertices) == 4:
                vertices = [vertices[0], vertices[1], vertices[3], vertices[2]]
            out += "<polygon points='"
            out += " ".join([f"{i},{j}" for i, j in vertices])
            out += "' fill='#BBEEFF' />"
    for n, edge in enumerate(reference.edges):
        p0 = to_2d(reference.vertices[edge[0]] + add)
        p1 = to_2d(reference.vertices[edge[1]] + add)
        if reference.name == "dual polygon":
            out += f"<line x1='{80 + float(p0[0])}' y1='{float(p0[1])}'"
            out += f" x2='{80 + float(p1[0])}' y2='{float(p1[1])}'"
        else:
            out += f"<line x1='{float(p0[0])}' y1='{float(p0[1])}'"
            out += f" x2='{float(p1[0])}' y2='{float(p1[1])}'"
        out += " stroke-width='4px' stroke-linecap='round' "
        if dof_entity == (1, n):
            out += "stroke='#44AAFF'"
        else:
            out += "stroke='#AAAAAA'"
        out += " />"
    return out


_mlcache = {}


def get_max_l(element, eval_points):
    reference = element.reference.name
    elementname = element.names[0]
    order = element.order
    if reference not in _mlcache:
        _mlcache[reference] = {}
    if elementname not in _mlcache[reference]:
        _mlcache[reference][elementname] = {}
    if order not in _mlcache[reference][elementname]:
        if element.range_dim == 1:
            max_l = 0
            for f in element.get_basis_functions():
                for p in eval_points:
                    r1 = subs(f, p)
                    max_l = max(max_l, r1)
        else:
            max_l = 0
            for f in element.get_basis_functions():
                for p in eval_points:
                    res = subs(f, p)
                    max_l = max(max_l, sum(i**2 for i in res) ** 0.5)

        _mlcache[reference][elementname][order] = max_l

    return _mlcache[reference][elementname][order]


def make_point_pairs(element, N=6):
    pairs = []
    if element.reference.tdim == 1:
        eval_points = make_lattice(element, N, False)
        pairs = [(i, i+1) for i, j in enumerate(eval_points[:-1])]
    elif element.reference.tdim == 2:
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
    return eval_points, pairs


def draw_function(element, dof_i):
    dof = element.dofs[dof_i]
    func = element.get_basis_functions()[dof_i]

    if isinstance(func, PiecewiseFunction):
        # TODO: Implement plotting of piecewise functions
        return ""

    if element.range_dim == 1 and element.reference.tdim not in [1, 2]:
        return ""
    if element.range_dim not in [1, element.domain_dim]:
        return ""

    if element.range_dim == 1:
        eval_points, pairs = make_point_pairs(element)
        add = (0, )
    else:
        eval_points = make_lattice(element, 6, True)
        add = tuple()

    max_l = get_max_l(element, eval_points)

    if element.reference.name == "hexahedron" or (
        element.range_dim == 1 and element.reference.name == "quadrilateral"
    ):
        out = "<svg width='215' height='200'>\n"
    else:
        out = "<svg width='200' height='200'>\n"
    out += draw_reference(element.reference, dof.entity, add)

    if element.range_dim != 1:
        for p in eval_points:
            res = subs(func, p)
            start = to_2d(p)
            end = to_2d([i + j * 0.4 / max_l for i, j in zip(p, res)])
            a1 = [end[0] + 0.25 * (start[0] - end[0]) - 0.12 * (start[1] - end[1]),
                  end[1] + 0.25 * (start[1] - end[1]) + 0.12 * (start[0] - end[0])]
            a2 = [end[0] + 0.25 * (start[0] - end[0]) + 0.12 * (start[1] - end[1]),
                  end[1] + 0.25 * (start[1] - end[1]) - 0.12 * (start[0] - end[0])]
            wid = 4 * sum(i**2 for i in res) ** 0.5 / max_l
            out += f"<line x1='{start[0]}' y1='{start[1]}' x2='{end[0]}' y2='{end[1]}'"
            out += f" stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"
            out += f"<line x1='{a1[0]}' y1='{a1[1]}' x2='{end[0]}' y2='{end[1]}'"
            out += f" stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"
            out += f"<line x1='{end[0]}' y1='{end[1]}' x2={a2[0]} y2={a2[1]}"
            out += f" stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"
    if dof.dof_direction() is None:
        out += dof_arrow(dof.dof_point() + add, None, dof_i, "#DD2299")
    else:
        out += dof_arrow(dof.dof_point() + add, dof.dof_direction() + add,
                         dof_i, "#DD2299")
    if element.range_dim == 1:
        if element.domain_dim == 1:
            eval_points, pairs = make_point_pairs(element, 2)

        for p, q in pairs:
            r1 = subs(func, eval_points[p])
            r2 = subs(func, eval_points[q])
            d_p1 = tuple(i + (j - i) / 3 for i, j in zip(eval_points[p], eval_points[q]))
            d_p2 = tuple(i + 2 * (j - i) / 3 for i, j in zip(eval_points[p], eval_points[q]))
            deriv = grad(func, element.domain_dim)
            d1 = vdot(subs(deriv, eval_points[p]), vsub(d_p1, eval_points[p]))
            d2 = vdot(subs(deriv, eval_points[q]), vsub(d_p2, eval_points[q]))
            start = to_2d(eval_points[p] + (r1 / max_l, ))
            end = to_2d(eval_points[q] + (r2 / max_l, ))
            mid1 = to_2d(d_p1 + ((d1 + r1) / max_l, ))
            mid2 = to_2d(d_p2 + ((d2 + r2) / max_l, ))
            out += f"<path d='M {start[0]} {start[1]} C {mid1[0]} {mid1[1]}, "
            out += f"{mid2[0]} {mid2[1]}, {end[0]} {end[1]}'"
            out += " stroke='#FF8800' stroke-width='2px' stroke-linecap='round' fill='none' />"

    out += "</svg>\n"
    return out


def draw_piecewise_function(element, func):
    if element.range_dim == 1 and element.reference.tdim not in [1, 2]:
        return ""
    if element.range_dim not in [1, element.domain_dim]:
        return ""

    if element.range_dim == 1:
        # eval_points, pairs = make_point_pairs(element)
        add = (0, )
    else:
        # eval_points = make_lattice(element, 6, True)
        add = tuple()

    max_l = 1  # get_max_l(element, eval_points)

    assert element.reference.name == "dual polygon"
    assert element.domain_dim == 2

    if element.range_dim == 1:
        out = "<svg width='300' height='200'>\n"
    else:
        out = "<svg width='300' height='300'>\n"
    out += draw_reference(element.reference, (-1, -1), add)

    if element.range_dim != 1:
        for vs, f in func.pieces:
            sub_e = create_element("triangle", element.fine_space, element.order)
            eval_points = make_lattice(sub_e, 3, True)
            eval_points = [tuple(subs(sub_e.reference.get_map_to(vs), p)) for p in eval_points]
            for p in eval_points:
                res = subs(f, p)
                start = to_2d(p)
                end = to_2d([i + j * 0.4 / max_l for i, j in zip(p, res)])
                a1 = [end[0] + 0.25 * (start[0] - end[0]) - 0.12 * (start[1] - end[1]),
                      end[1] + 0.25 * (start[1] - end[1]) + 0.12 * (start[0] - end[0])]
                a2 = [end[0] + 0.25 * (start[0] - end[0]) + 0.12 * (start[1] - end[1]),
                      end[1] + 0.25 * (start[1] - end[1]) - 0.12 * (start[0] - end[0])]
                wid = 4 * sum(i**2 for i in res) ** 0.5 / max_l
                out += f"<line x1='{start[0] + 80}' y1='{start[1]}'"
                out += f" x2='{end[0] + 80}' y2='{end[1]}'"
                out += f" stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"
                out += f"<line x1='{a1[0] + 80}' y1='{a1[1]}' x2='{end[0] + 80}' y2='{end[1]}'"
                out += f" stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"
                out += f"<line x1='{end[0] + 80}' y1='{end[1]}' x2={a2[0] + 80} y2={a2[1]}"
                out += f" stroke='#FF8800' stroke-width='{wid}px' stroke-linecap='round' />"

    # if dof.dof_direction() is None:
    #    out += dof_arrow(dof.dof_point() + add, None, dof_i, "#DD2299")
    # else:
    #    out += dof_arrow(dof.dof_point() + add, dof.dof_direction() + add,
    #                     dof_i, "#DD2299")

    if element.range_dim == 1:
        for vs, f in func.pieces:
            sub_e = create_element("triangle", element.fine_space, element.order)
            eval_points, pairs = make_point_pairs(sub_e, 3)
            eval_points = [tuple(subs(sub_e.reference.get_map_to(vs), p)) for p in eval_points]

            for p, q in pairs:
                r1 = subs(f, eval_points[p])
                r2 = subs(f, eval_points[q])
                d_p1 = tuple(i + (j - i) / 3 for i, j in zip(eval_points[p], eval_points[q]))
                d_p2 = tuple(i + 2 * (j - i) / 3 for i, j in zip(eval_points[p], eval_points[q]))
                deriv = grad(f, element.domain_dim)
                d1 = vdot(subs(deriv, eval_points[p]), vsub(d_p1, eval_points[p]))
                d2 = vdot(subs(deriv, eval_points[q]), vsub(d_p2, eval_points[q]))
                start = to_2d(eval_points[p] + (r1 / max_l, ))
                end = to_2d(eval_points[q] + (r2 / max_l, ))
                mid1 = to_2d(d_p1 + ((d1 + r1) / max_l, ))
                mid2 = to_2d(d_p2 + ((d2 + r2) / max_l, ))
                out += f"<path d='M {start[0] + 80} {start[1]} C {mid1[0] + 80} {mid1[1]}, "
                out += f"{mid2[0] + 80} {mid2[1]}, {end[0] + 80} {end[1]}'"
                out += " stroke='#FF8800' stroke-width='2px' stroke-linecap='round' fill='none' />"
    out += "</svg>\n"
    return out


def markup_element(element):
    eg = ""
    eg += "<ul>\n"
    # Reference
    eg += f"<li>\\({symbols.reference}\\) is the reference {element.reference.name}."
    eg += " The following numbering of the subentities of the reference is used:</li>\n"
    eg += "<center>" + svg_reference(element.reference) + "</center>\n"
    # Polynomial set
    if element.reference.name != "dual polygon":
        eg += f"<li>\\({symbols.polyset}\\) is spanned by: "
        eg += ", ".join(["\\(" + to_tex(i) + "\\)" for i in element.get_polynomial_basis()])
        eg += "</li>\n"
    # Dual basis
    if element.reference.name != "dual polygon":
        eg += f"<li>\\({symbols.dual_basis}=\\{{{symbols.functional}_0,"
        eg += f"...,{symbols.functional}_{{{len(element.dofs) - 1}}}\\}}\\)</li>\n"

    # Basis functions
    if element.reference.name == "dual polygon":
        eg += "<li>Basis functions:</li>"
    else:
        eg += "<li>Functionals and basis functions:</li>"
    eg += "</ul>"

    if element.reference.name == "dual polygon":
        for f in element.get_basis_functions():
            eg += "<div class='basisf'><div style='display:inline-block'>"
            eg += draw_piecewise_function(element, f)
            eg += "</div>"
            eg += "</div>"
    else:
        for dof_i, (dof, func) in enumerate(zip(element.dofs, element.get_basis_functions())):
            eg += "<div class='basisf'><div style='display:inline-block'>"
            eg += draw_function(element, dof_i)
            eg += "</div>"
            eg += "<div style='display:inline-block;padding-left:10px;padding-bottom:10px'>"
            eg += f"\\(\\displaystyle {symbols.functional}_{{{dof_i}}}:"
            eg += describe_dof(element, dof) + "\\)<br /><br />"
            if element.range_dim == 1:
                eg += f"\\(\\displaystyle {symbols.basis_function}_{{{dof_i}}} = "
            elif element.range_shape is None or len(element.range_shape) == 1:
                eg += f"\\(\\displaystyle {symbols.vector_basis_function}_{{{dof_i}}} = "
            else:
                eg += f"\\(\\displaystyle {symbols.matrix_basis_function}_{{{dof_i}}} = "
            eg += to_tex(func) + "\\)<br /><br />"
            eg += "This DOF is associated with "
            eg += ["vertex", "edge", "face", "volume"][dof.entity[0]] + f" {dof.entity[1]}"
            eg += " of the reference element.</div></div>"

    return eg


def dof_arrow(point, dir, n, color="#000000", width=200, height=200, map_to_2d=True):
    out = ""
    if map_to_2d:
        start = to_2d(tuple(float(i) for i in point), width=width, height=height)
    else:
        assert dir is None
        start = point
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
