import os
import sympy
from symfem.finite_element import CiarletElement, DirectElement
from symfem.functions import AnyFunction
from symfem.symbols import t
from .html import make_html_page
from .markup import heading_with_self_ref
from . import settings, symbols, plotting

defelement_t = ["s_{0}", "s_{1}", "s_{2}"]


def to_tex(f, tfrac=False):
    if isinstance(f, (list, tuple)):
        return "\\left(\\begin{array}{c}" + "\\\\".join(
            ["\\displaystyle " + to_tex(i) for i in f]) + "\\end{array}\\right)"
    elif isinstance(f, AnyFunction):
        out = f.as_tex()
    else:
        out = sympy.latex(sympy.simplify(sympy.expand(f)))
        out = out.replace("\\left[", "\\left(")
        out = out.replace("\\right]", "\\right)")

        for i, j in zip(t, defelement_t):
            out = out.replace(sympy.latex(i), j)

    if tfrac:
        return out.replace("\\frac", "\\tfrac")
    else:
        return out


def entity_name(dim):
    return ["vertex", "edge", "face", "volume"][dim]


def describe_dof(element, d):
    desc, symb = d.get_tex()

    for i, j in zip(t, defelement_t):
        desc = desc.replace(sympy.latex(i), j)

    for j in defelement_t:
        if j in desc:
            dim = element.reference.tdim
            new_s = "\\("
            if dim == 1:
                new_s += defelement_t[0]
            else:
                new_s += ','.join(defelement_t[:dim])
            new_s += f"\\) is a parametrisation of \\({symb[0]}\\)"
            symb.append(new_s)
            break

    return desc, symb


def markup_example(element, html_name, element_page, fname):
    eg = heading_with_self_ref(
        "h1", f"Degree {element.order} {html_name} on a {element.reference.name}")
    eg += "\n"
    eg += f"<a href='{element_page}'><small>&#9664; Back to {html_name} definition page"
    eg += "</a></small>\n"
    eg += "<center>" + plotting.plot_dof_diagram(element) + "</center>\n"
    eg += "In this example:\n<ul>\n"
    # Reference
    eg += f"<li>\\({symbols.reference}\\) is the reference {element.reference.name}."
    eg += " The following numbering of the subentities of the reference is used:</li>\n"
    eg += "<center>" + plotting.plot_reference(element.reference) + "</center>\n"
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
        if plots[dof_i] is not None:
            eg += plots[dof_i]
        eg += "</div>"
        eg += "<div style='display:inline-block;padding-left:10px;padding-bottom:10px'>"
        if isinstance(element, CiarletElement) and len(element.dofs) > 0:
            dof = element.dofs[dof_i]
            eg += f"\\(\\displaystyle {symbols.functional}_{{{dof_i}}}:"
            dof_tex, symbols_used = describe_dof(element, dof)
            eg += dof_tex + "\\)"
            if len(symbols_used) > 0:
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

    with open(os.path.join(os.path.join(settings.htmlelement_path, "examples", fname)), "w") as f:
        f.write(make_html_page(eg))

    return f"/elements/examples/{fname}"
