from . import symbols
from . import plotting
import sympy
from symfem.core import functionals
from symfem.core.symbolic import PiecewiseFunction


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
    if isinstance(d, functionals.WeightedPointEvaluation):
        desc = f"v\\mapsto " + to_tex(d.weight)
        desc += " v(" + ",".join([to_tex(i, True) for i in d.dof_point()]) + ")"
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


def markup_example(element):
    eg = ""
    eg += "<ul>\n"
    # Reference
    eg += f"<li>\\({symbols.reference}\\) is the reference {element.reference.name}."
    eg += " The following numbering of the subentities of the reference is used:</li>\n"
    eg += "<center>" + plotting.plot_reference(element.reference).img_html() + "</center>\n"
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

    plots = plotting.plot_basis_functions(element)

    for dof_i, func in enumerate(element.get_basis_functions()):
        eg += "<div class='basisf'><div style='display:inline-block'>"
        eg += plots[dof_i].img_html()
        eg += "</div>"
        if len(element.dofs) > 0:
            dof = element.dofs[dof_i]
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
            eg += " of the reference element.</div>"
        eg += "</div>"

    return eg
