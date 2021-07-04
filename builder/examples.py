from . import symbols
from . import plotting
import sympy
from symfem import functionals
from symfem.symbolic import PiecewiseFunction, t
from symfem.finite_element import CiarletElement, DirectElement

defelement_t = ["s_{0}", "s_{1}", "s_{2}"]


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

    for i, j in zip(t, defelement_t):
        out = out.replace(sympy.latex(i), j)

    if tfrac:
        return out.replace("\\frac", "\\tfrac")
    else:
        return out


def get_entity_number(element, dof):
    if dof.entity_dim() == 1:
        entities = element.reference.edges
    elif dof.entity_dim() == 2:
        entities = element.reference.faces
    elif dof.entity_dim() == 3:
        entities = element.reference.volumes
    return str(entities.index(
        tuple(element.reference.vertices.index(i)
              for i in dof.reference.vertices)))


def entity_name(dim):
    return ["vertex", "edge", "face", "volume"][dim]


def nth(n):
    if n % 10 == 1 and n != 11:
        return f"{n}st"
    if n % 10 == 2 and n != 12:
        return f"{n}nd"
    return f"{n}th"


def define_symbol(symbol):
    for dim in range(4):
        for i in range(12):
            if symbol == f"{symbols.entity(dim)}_{{{i}}}":
                return f"\\({symbol}\\) is the {nth(i)} {entity_name(dim)}"

    for i in range(12):
        if symbol == f"\\hat{{\\boldsymbol{{n}}}}_{{{i}}}":
            return f"\\({symbol}\\) is the normal to facet {i}"

    for i in range(12):
        if symbol == f"\\hat{{\\boldsymbol{{t}}}}_{{{i}}}":
            return f"\\({symbol}\\) is the tangent to edge {i}"

    if symbol == "R":
        return f"\\({symbol}\\) is the reference element"

    if symbol[:5] == "param":
        for dim in range(4):
            for i in range(12):
                if symbol[5:] in [f"{symbols.entity(dim)}_{{{i}}}", f"R({dim})"]:
                    if symbol[5] == f"R({dim})":
                        ref = "R"
                    else:
                        ref = symbol[5:]
                    assert dim > 0
                    if dim == 1:
                        return (f"\\({defelement_t[0]}\\)"
                                f" is a parametrisation of \\({ref}\\)")
                    else:
                        return (f"\\(({','.join(defelement_t[:dim])})\\)"
                                f" is a parametrisation of \\({ref}\\)")

    raise ValueError(f"Unrecognised symbol: {symbol}")


def describe_dof(element, d):
    desc, symb = _describe_dof(element, d)
    for i in defelement_t:
        if i in desc:
            if symb[0] == "R":
                symb.append(f"paramR({element.reference.tdim})")
            else:
                symb.append("param" + symb[0])
            break
    return desc, symb


def _describe_dof(element, d):
    if isinstance(d, functionals.PointEvaluation):
        return "v\\mapsto v(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")", []
    elif isinstance(d, functionals.DotPointEvaluation):
        desc = "\\boldsymbol{v}\\mapsto"
        desc += "\\boldsymbol{v}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        desc += "\\cdot\\left(\\begin{array}{c}"
        desc += "\\\\".join([to_tex(i) for i in d.dof_direction()])
        desc += "\\end{array}\\right)"
        return desc, []
    if isinstance(d, functionals.WeightedPointEvaluation):
        desc = f"v\\mapsto " + to_tex(d.weight)
        desc += " v(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        return desc, []
    elif isinstance(d, functionals.PointNormalDerivativeEvaluation):
        desc = "v\\mapsto"
        desc += "\\nabla{v}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        entity_n = get_entity_number(element, d)
        desc += "\\cdot\\hat{\\boldsymbol{n}}" + f"_{{{entity_n}}}"
        return desc, ["\\hat{\\boldsymbol{n}}" + f"_{{{entity_n}}}"]
    elif isinstance(d, functionals.PointDirectionalDerivativeEvaluation):
        if element.reference.tdim == 1:
            desc = "v\\mapsto "
            desc += "v'(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
            return desc, []
        desc = "v\\mapsto"
        desc += "\\nabla{v}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        desc += "\\cdot\\left(\\begin{array}{c}"
        desc += "\\\\".join([to_tex(i) for i in d.dof_direction()])
        desc += "\\end{array}\\right)"
        return desc, []
    elif isinstance(d, functionals.DerivativePointEvaluation):
        if element.reference.tdim == 1:
            desc = "v\\mapsto "
            desc += "v'(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
            return desc, []
        desc = "v\\mapsto"
        desc += "\\frac{\\partial"
        if sum(d.derivative) > 1:
            desc += f"^{{{sum(d.derivative)}}}"
        desc += "}{"
        for v, i in zip("xyz", d.derivative):
            if i > 0:
                desc += f"\\partial {v}"
                if i > 1:
                    desc += f"^{{{i}}}"
        desc += "}"
        desc += "\\nabla{v}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        return desc, []
    elif isinstance(d, functionals.PointComponentSecondDerivativeEvaluation):
        desc = "v\\mapsto"
        desc += "\\frac{\\partial^2v}{"
        for c in d.component:
            desc += "\\partial " + "xyz"[c]
        desc += "}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        return desc, []
    elif isinstance(d, functionals.TangentIntegralMoment):
        entity = symbols.entity(d.entity_dim())
        entity_n = get_entity_number(element, d)
        desc = "\\boldsymbol{v}\\mapsto"
        desc += f"\\displaystyle\\int_{{{entity}_{{{entity_n}}}}}"
        desc += "\\boldsymbol{v}\\cdot"
        if d.f != 1:
            desc += "(" + to_tex(d.f) + ")"
        desc += "\\hat{\\boldsymbol{t}}" + f"_{{{entity_n}}}"
        return desc, [f"{entity}_{{{entity_n}}}", "\\hat{\\boldsymbol{t}}" + f"_{{{entity_n}}}"]
    elif isinstance(d, functionals.NormalIntegralMoment):
        entity = symbols.entity(d.entity_dim())
        entity_n = get_entity_number(element, d)
        desc = "\\boldsymbol{v}\\mapsto"
        desc += f"\\displaystyle\\int_{{{entity}_{{{entity_n}}}}}"
        desc += "\\boldsymbol{v}\\cdot"
        if d.f != 1:
            desc += "(" + to_tex(d.f, True) + ")"
        desc += "\\hat{\\boldsymbol{n}}" + f"_{{{entity_n}}}"
        return desc, [f"{entity}_{{{entity_n}}}", "\\hat{\\boldsymbol{n}}" + f"_{{{entity_n}}}"]
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
        return desc, [f"{entity}_{{{entity_n}}}", "\\hat{\\boldsymbol{n}}" + f"_{{{entity_n}}}"]
    elif isinstance(d, functionals.IntegralAgainst):
        entity = symbols.entity(d.entity_dim())
        entity_n = get_entity_number(element, d)
        desc = "\\mathbf{V}\\mapsto"
        desc += f"\\displaystyle\\int_{{{entity}_{{{entity_n}}}}}"
        if d.f != 1:
            desc += "(" + to_tex(d.f, True) + ")"
        desc += "v"
        return desc, [f"{entity}_{{{entity_n}}}"]
    elif isinstance(d, functionals.IntegralOfDirectionalMultiderivative):
        entity = symbols.entity(d.entity_dim())
        entity_n = get_entity_number(element, d)
        desc = "\\mathbf{V}\\mapsto"
        desc += "\\displaystyle"
        if d.scale != 1:
            desc += to_tex(d.scale)
        desc += f"\\int_{{{entity}_{{{entity_n}}}}}"
        for order, dir in zip(d.orders, d.directions):
            if order > 0:
                desc += "\\frac{\\partial"
                if order > 1:
                    desc += f"^{{{order}}}"
                desc += "}{"
                desc += "\\partial" + to_tex(dir)
                if order > 1:
                    desc += f"^{{{order}}}"
                desc += "}"
        desc += "v"
        return desc, [f"{entity}_{{{entity_n}}}"]
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
        return desc, [f"{entity}"]
    elif isinstance(d, functionals.PointInnerProduct):
        desc = "\\mathbf{V}\\mapsto"
        desc += "\\left(\\begin{array}{c}"
        desc += "\\\\".join([to_tex(i) for i in d.lvec])
        desc += "\\end{array}\\right)^t"
        desc += "\\mathbf{V}(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
        desc += "\\left(\\begin{array}{c}"
        desc += "\\\\".join([to_tex(i) for i in d.rvec])
        desc += "\\end{array}\\right)"
        return desc, []
    else:
        raise ValueError(f"Unknown functional: {d.__class__}")


def markup_example(element):
    eg = ""
    eg += "<ul>\n"
    # Reference
    eg += f"<li>\\({symbols.reference}\\) is the reference {element.reference.name}."
    eg += " The following numbering of the subentities of the reference is used:</li>\n"
    eg += "<center>" + plotting.plot_reference(element.reference).img_html() + "</center>\n"
    if isinstance(element, CiarletElement) and element.reference.name != "dual polygon":
        # Polynomial set
        eg += f"<li>\\({symbols.polyset}\\) is spanned by: "
        eg += ", ".join(["\\(" + to_tex(i) + "\\)" for i in element.get_polynomial_basis()])
        eg += "</li>\n"

        # Dual basis
        eg += f"<li>\\({symbols.dual_basis}=\\{{{symbols.functional}_0,"
        eg += f"...,{symbols.functional}_{{{len(element.dofs) - 1}}}\\}}\\)</li>\n"

    # Basis functions
    if not isinstance(element, CiarletElement) or element.reference.name == "dual polygon":
        eg += "<li>Basis functions:</li>"
    else:
        eg += "<li>Functionals and basis functions:</li>"
    eg += "</ul>"

    plots = plotting.plot_basis_functions(element)

    for dof_i, func in enumerate(element.get_basis_functions()):
        eg += "<div class='basisf'><div style='display:inline-block'>"
        eg += plots[dof_i].img_html()
        eg += "</div>"
        eg += "<div style='display:inline-block;padding-left:10px;padding-bottom:10px'>"
        if isinstance(element, CiarletElement) and len(element.dofs) > 0:
            dof = element.dofs[dof_i]
            eg += f"\\(\\displaystyle {symbols.functional}_{{{dof_i}}}:"
            dof_tex, symbols_used = describe_dof(element, dof)
            symbols_used += []
            eg += dof_tex + "\\)"
            if len(symbols_used) > 0:
                symbols_used = [define_symbol(i) for i in symbols_used]
                eg += "<br />where " + ";<br />".join(symbols_used[:-1])
                if len(symbols_used) > 1:
                    eg += ";<br />and "
                eg += symbols_used[-1] + "."
            eg += "<br /><br />"
        if element.range_dim == 1:
            eg += f"\\(\\displaystyle {symbols.basis_function}_{{{dof_i}}} = "
        elif element.range_shape is None or len(element.range_shape) == 1:
            eg += f"\\(\\displaystyle {symbols.vector_basis_function}_{{{dof_i}}} = "
        else:
            eg += f"\\(\\displaystyle {symbols.matrix_basis_function}_{{{dof_i}}} = "
        eg += to_tex(func) + "\\)"
        if isinstance(element, CiarletElement):
            if len(element.dofs) > 0:
                eg += "<br /><br />"
                eg += "This DOF is associated with "
                eg += entity_name(dof.entity[0]) + f" {dof.entity[1]}"
                eg += " of the reference element."
        elif isinstance(element, DirectElement):
            eg += "<br /><br />"
            eg += "This DOF is associated with "
            eg += entity_name(element._basis_entities[dof_i][0])
            eg += f" {element._basis_entities[dof_i][1]}"
            eg += " of the reference element."
        eg += "</div>"
        eg += "</div>"

    return eg
