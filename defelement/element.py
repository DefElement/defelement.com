"""DefElement elements."""

import os
import typing
import warnings
from datetime import datetime

import pytz
import yaml
from github import Github

from defelement import settings
from defelement.families import arnold_logg_reference, cockburn_fu_reference, keys_and_names
from defelement.implementations import VariantNotImplemented, examples, implementations
from defelement.markup import insert_links
from defelement.polyset import make_extra_info, make_poly_set


def make_dof_data(
    ndofs: typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Dict[str, typing.Any]]]
) -> str:
    """Make DOF data.

    Args:
        ndofs: DOF information

    Returns:
        DOFs formatted as HTML
    """
    if isinstance(ndofs, list):
        return "<br /><br />".join([f"\\({i}\\):<br />{make_dof_data(j)}"
                                    for a in ndofs for i, j in a.items()])

    dof_text = []
    for i, j in ndofs.items():
        txt = f"{i}: "
        txt += make_formula(j)
        dof_text.append(txt)

    return "<br />".join(dof_text)


def make_formula(data: typing.Dict[str, typing.Any]) -> str:
    """Make formula.

    Args:
        data: Element data

    Returns:
        Formula for number of DOFs in HTML format
    """
    txt = ""
    if "formula" not in data and "oeis" not in data:
        return ", ".join(f"{make_formula(j)} ({i})"
                         for i, j in data.items())
    if "formula" in data:
        txt += "\\("
        if isinstance(data["formula"], list):
            txt += "\\begin{cases}"
            txt += "\\\\".join([f"{c}&{b}" for a in data["formula"] for b, c in a.items()])
            txt += "\\end{cases}"
        else:
            txt += f"{data['formula']}"
        txt += "\\)"
    if "oeis" in data:
        if "formula" in data:
            txt += " ("
        txt += f"<a href='http://oeis.org/{data['oeis']}'>{data['oeis']}</a>"
        if "formula" in data:
            txt += ")"
    return txt


class Element:
    """An element."""

    def __init__(self, data: typing.Dict[str, typing.Any], fname: str):
        """Initialise.

        Args:
            data: element data
            fname: filename
        """
        self.data = data
        self.filename = fname
        self._c: typing.Optional[Categoriser] = None
        self.created = None
        self.modified = None

    def name_with_variant(self, variant: typing.Optional[str]) -> str:
        """Get name with variant.

        Args:
            variant: The variant

        Return:
            Name with variant
        """
        if variant is None:
            return self.name
        return f"{self.name} ({self.variant_name(variant)} variant)"

    def variant_name(self, variant: str) -> str:
        """Get variant name.

        Args:
            variant: The variant

        Returns:
            The variant name
        """
        return self.data["variants"][variant]["variant-name"]

    def variants(self) -> typing.List[str]:
        """Get variants of the element.

        Returns:
            A list of variants
        """
        if "variants" not in self.data:
            return []
        return [
            f"{v['variant-name']}: {v['description']}"
            for v in self.data["variants"].values()
        ]

    def min_degree(self, ref: str) -> int:
        """Get the minimum degree.

        Args:
            ref: Reference cell

        Returns:
            The minimum degree
        """
        if "min-degree" not in self.data:
            return 0
        if isinstance(self.data["min-degree"], dict):
            return self.data["min-degree"][ref]
        return self.data["min-degree"]

    def max_degree(self, ref: str) -> typing.Optional[int]:
        """Get the maximum degree.

        Args:
            ref: Reference cell

        Returns:
            The maximum degree
        """
        if "max-degree" not in self.data:
            return None
        if isinstance(self.data["max-degree"], dict):
            return self.data["max-degree"][ref]
        return self.data["max-degree"]

    def degree_convention(self) -> typing.Optional[str]:
        """Get the degree convention.

        returns:
            The degree convention
        """
        if "degree" not in self.data:
            return None
        return self.data["degree"]

    def _edegree(self, dtype: str) -> typing.Optional[str]:
        """Get an embedded degree.

        returns:
            Information about the embedded degree
        """
        if dtype not in self.data:
            return None

        def to_tex(txt):
            txt = str(txt)
            if txt == "none":
                return "undefined"
            txt = txt.replace("floor", "\\operatorname{floor}")
            txt = txt.replace("min", "\\min")
            txt = txt.replace("max", "\\max")
            return f"\\({txt}\\)"

        d = self.data[dtype]
        if isinstance(d, dict):
            return "<br />".join([
                f"{cell}: {to_tex(deg)}"
                for cell, deg in d.items()
            ])
        return to_tex(d)

    def polynomial_subdegree(self) -> typing.Optional[str]:
        """Get the polynomial subdegree.

        returns:
            The degree convention
        """
        return self._edegree("polynomial-subdegree")

    def polynomial_superdegree(self) -> typing.Optional[str]:
        """Get the polynomial superdegree.

        returns:
            The degree convention
        """
        return self._edegree("polynomial-superdegree")

    def lagrange_subdegree(self) -> typing.Optional[str]:
        """Get the Lagrange subdegree.

        returns:
            The degree convention
        """
        return self._edegree("lagrange-subdegree")

    def lagrange_superdegree(self) -> typing.Optional[str]:
        """Get the polynomial superdegree.

        returns:
            The degree convention
        """
        return self._edegree("lagrange-superdegree")

    def reference_elements(self, link: bool = True) -> typing.List[str]:
        """Get reference cells.

        Args:
            link: Should a link be included?

        Returns:
            List of reference cells.
        """
        if link:
            return [f"<a href='/lists/references/{e}.html'>{e}</a>"
                    for e in self.data["reference-elements"]]
        else:
            return self.data["reference-elements"]

    def alternative_names(
        self, include_bracketed: bool = True, include_complexes: bool = True,
        include_variants: bool = True, link: bool = True,
        strip_cell_name: bool = False, cell: typing.Optional[str] = None
    ) -> typing.List[str]:
        """Get alternative names.

        Args:
            include_bracketed: Should bracketed names be included?
            include_complexes: Should names complexes be included?
            include_variants: Should variants be included?
            link: Should the names be linked?
            strip_cell_names: Should cell names be stripped?
            cell: Reference cell

        Returns:
            A list of names
        """
        if "alt-names" not in self.data:
            return []
        out = self.data["alt-names"]
        if include_complexes:
            out += self.complexes(link=link)
        if include_variants and "variants" in self.data:
            for v in self.data["variants"].values():
                if "names" in v:
                    out += [f"{i} ({v['variant-name']} variant)" for i in v["names"]]

        if include_bracketed:
            out = [i[1:-1] if i[0] == "(" and i[-1] == ")" else i
                   for i in out]
        else:
            out = [i for i in out if i[0] != "(" or i[-1] != ")"]

        if cell is not None:
            out = [i for i in out if " (" not in i or cell in i]

        if strip_cell_name:
            out = [i.split(" (")[0] for i in out]

        return out

    def short_names(self, include_variants: bool = True) -> typing.List[str]:
        """Get short names.

        Args:
            include_variants: Should variants be included?

        Returns:
            A list of short names
        """
        out = []
        if "short-names" in self.data:
            out += self.data["short-names"]
        if include_variants and "variants" in self.data:
            for v in self.data["variants"].values():
                if "short-names" in v:
                    out += [f"{i} ({v['variant-name']} variant)" for i in v["short-names"]]
        return out

    def mapping(self) -> typing.Union[None, str]:
        """Get mapping name.

        Returns:
            Mapping name
        """
        if "mapping" not in self.data:
            return None
        return self.data["mapping"]

    def sobolev(self) -> typing.Union[None, str]:
        """Get Sobolev space name.

        Returns:
            Sobolev space
        """
        if "sobolev" not in self.data:
            return None
        return self.data["sobolev"]

    def complexes(
        self, link: bool = True, names: bool = True
    ) -> typing.Dict[str, typing.List[str]]:
        """Get complexes.

        Args:
            link: Should links be included?
            names: Should names be used?

        Returns:
            Complexes
        """
        assert self._c is not None

        if "complexes" not in self.data:
            return {}

        out: typing.Dict[str, typing.List[str]] = {}
        com = self.data["complexes"]
        for key, families in com.items():
            out[key] = []
            if not isinstance(families, (list, tuple)):
                families = [families]
            for e in families:
                if names:
                    namelist = []
                    e_s = e.split(",")
                    if len(e_s) == 3:
                        fam, ext, cell = e_s
                        k = "k"
                    else:
                        fam, ext, cell, k = e_s
                    data = self._c.families[key][fam]
                    for key2, f in keys_and_names:
                        if key2 in data:
                            namelist.append("\\(" + f(data[key2], ext, cell, k) + "\\)")
                    entry = ""
                    if link:
                        entry = f"<a class='nou' href='/families/{fam}.html'>"
                    entry += " or ".join(namelist)
                    if link:
                        entry += "</a>"
                    out[key].append(entry)
                else:
                    out[key].append(e)
        return out

    def degree_range(self) -> str:
        """Format the range of allowed degrees.

        Returns:
            The formatted range
        """
        def make_degree_data(
            min_o: typing.Union[typing.Dict[str, int], int, None],
            max_o: typing.Union[typing.Dict[str, int], int, None]
        ) -> str:
            """Make degree data.

            Args:
                min_o: The minimum degree
                max_o: The maximum degree

            Returns:
                The formatted degree
            """
            if isinstance(min_o, dict):
                degrees = []
                for i, min_i in min_o.items():
                    if isinstance(max_o, dict) and i in max_o:
                        degrees.append(i + ": " + make_degree_data(min_i, max_o[i]))
                    else:
                        degrees.append(i + ": " + make_degree_data(min_i, max_o))
                return "<br />\n".join(degrees)
            if isinstance(max_o, dict):
                degrees = []
                for i, max_i in max_o.items():
                    degrees.append(i + ": " + make_degree_data(min_o, max_i))
                return "<br />\n".join(degrees)
            if max_o is None:
                return f"\\({min_o}\\leqslant k\\)"
            if max_o == min_o:
                return f"\\(k={min_o}\\)"
            return f"\\({min_o}\\leqslant k\\leqslant {max_o}\\)"

        return make_degree_data(
            self.data["min-degree"] if "min-degree" in self.data else 0,
            self.data["max-degree"] if "max-degree" in self.data else None)

    def sub_elements(self, link: bool = True) -> typing.List[str]:
        """Get sub elements of a mixed element.

        Args:
            link: Should a link be included?

        Returns:
            List of sub-elements
        """
        assert self.is_mixed
        assert self._c is not None

        out = []
        for e in self.data["mixed"]:
            element, degree = e.split("(")
            degree = degree.split(")")[0]
            space_link = self._c.get_space_name(element, link=link)
            out.append(f"<li>degree \\({degree}\\) {space_link} space</li>")
        return out

    def make_dof_descriptions(self) -> str:
        """Make DOF descroptions.

        Returns:
            Descriptions of DOFs
        """
        if "dofs" not in self.data:
            return ""

        def dofs_on_entity(
            entity: str, dofs: typing.Union[str, typing.List[str]]
        ) -> str:
            """Get DOFs on an entity.

            Args:
                entity: The entity name
                dofs: The dofs

            Returns:
                Formatted DOFs
            """
            assert self._c is not None
            if not isinstance(dofs, str):
                doflist = [dofs_on_entity(entity, d) for d in dofs]
                return ",<br />".join(doflist[:-1]) + ", and " + doflist[-1]
            if "integral moment" in dofs:
                mom_type, space_info = dofs.split(" with ")
                space_info = space_info.strip()
                if space_info.startswith("{") and space_info.endswith("}"):
                    return f"{mom_type} with \\(\\left\\{{{space_info[1:-1]}\\right\\}}\\)"
                if space_info.startswith('"') and space_info.endswith('"'):
                    return f"{mom_type} with {insert_links(space_info[1:-1])}"

                assert space_info.startswith("(") and space_info.endswith(")")
                space_info = space_info[1:-1]
                space, degree = space_info.split(",")
                space = space.strip()
                degree = degree.strip()
                space_link = self._c.get_space_name(space)
                return f"{mom_type} with an degree \\({degree}\\) {space_link} space"
            return dofs

        def make_dof_d(data: typing.Dict[str, typing.Any], post: str = "") -> str:
            """Make a decription of a single DOF.

            Args:
                data: Data
                post: String to include after DOF name

            Returns:
                Formatted DOF
            """
            dof_data = []
            for i in ["interval", "triangle", "tetrahedron", "quadrilateral", "hexahedron"]:
                if i in data:
                    dof_data.append(make_dof_d(data[i], f" ({i})"))
            if len(dof_data) != 0:
                return "<br />\n<br />\n".join(dof_data)

            for i, j in [
                ("On each vertex", "vertices"),
                ("On each edge", "edges"),
                ("On each face", "faces"),
                ("On each volume", "volumes"),
                ("On each ridge", "ridges"),
                ("On each peak", "peaks"),
                ("On each facet", "facets"),
                ("On the interior of the reference element", "cell"),
            ]:
                if j in data:
                    if isinstance(data[j], dict):
                        for shape, sub_data in data[j].items():
                            dof_data.append(f"{i} ({shape}){post}: {dofs_on_entity(j, sub_data)}")
                    else:
                        dof_data.append(f"{i}{post}: {dofs_on_entity(j, data[j])}")
            return "<br />\n".join(dof_data)

        return make_dof_d(self.data["dofs"])

    def make_polynomial_set_html(self) -> str:
        """Format polynomial set as HTML.

        Returns:
            Formatted polynomial set
        """
        # TODO: move some of this to polynomial file
        if "polynomial-set" not in self.data:
            return ""
        psets: typing.Dict[str, typing.List[str]] = {}
        for i, j in self.data["polynomial-set"].items():
            if j not in psets:
                psets[j] = []
            psets[j].append(i)
        if (
            "reference-elements" in self.data and len(psets) == 1
            and len(list(psets.values())[0]) == len(self.data["reference-elements"])
        ):
            out = f"\\({make_poly_set(list(psets.keys())[0])}\\)<br />"
        else:
            out = ""
            for i, j in psets.items():
                out += f"\\({make_poly_set(i)}\\) ({', '.join(j)})<br />\n"
        extra = make_extra_info(" && ".join(psets.keys()))
        if len(extra) > 0:
            out += "<a id='show_pset_link' href='javascript:show_psets()'"
            out += " style='display:block'>"
            out += "&darr; Show polynomial set definitions &darr;</a>"
            out += "<a id='hide_pset_link' href='javascript:hide_psets()'"
            out += " style='display:none'>"
            out += "&uarr; Hide polynomial set definitions &uarr;</a>"
            out += "<div id='psets' style='display:none'>"
            out += extra
            out += "</div>"
            out += "<script type='text/javascript'>\n"
            out += "function show_psets(){\n"
            out += "  document.getElementById('show_pset_link').style.display = 'none'\n"
            out += "  document.getElementById('hide_pset_link').style.display = 'block'\n"
            out += "  document.getElementById('psets').style.display = 'block'\n"
            out += "}\n"
            out += "function hide_psets(){\n"
            out += "  document.getElementById('show_pset_link').style.display = 'block'\n"
            out += "  document.getElementById('hide_pset_link').style.display = 'none'\n"
            out += "  document.getElementById('psets').style.display = 'none'\n"
            out += "}\n"
            out += "</script>"
        return out

    def dof_counts(self) -> str:
        """Get DOF counts.

        Returns:
            DOF counts
        """
        if "ndofs" not in self.data:
            return ""
        return make_dof_data(self.data["ndofs"])

    def entity_dof_counts(self) -> str:
        """Get entity DOF counts.

        Returns:
            Entity DOF counts
        """
        if "entity-ndofs" not in self.data:
            return ""
        return make_dof_data(self.data["entity-ndofs"])

    @property
    def name(self) -> str:
        """Get element name.

        Returns:
            The element name
        """
        return self.data["name"]

    @property
    def notes(self) -> typing.List[str]:
        """Get notes.

        Returns:
            notes
        """
        if "notes" not in self.data:
            return []
        return self.data["notes"]

    @property
    def html_name(self) -> str:
        """Get HTML name.

        Returns:
            The HTML name
        """
        if "html-name" in self.data:
            return self.data["html-name"]
        else:
            return self.data["name"]

    @property
    def html_filename(self) -> str:
        """Get HTML filename.

        Returns:
            The filename
        """
        return f"{self.filename}.html"

    @property
    def is_mixed(self) -> bool:
        """Check if element is mixed.

        Returns:
            True if mixed, otherwise False
        """
        return "mixed" in self.data

    @property
    def html_link(self) -> str:
        """Get link to element.

        Returns:
            Link to this element
        """
        return f"<a href='/elements/{self.html_filename}'>{self.html_name}</a>"

    def implemented(self, lib: str) -> bool:
        """Check if element in implemented in a library.

        Args:
            lib: The library

        Returns:
            True if implemented, otherwise False
        """
        return "implementations" in self.data and lib in self.data["implementations"]

    def get_implementation_string(
        self, lib: str, reference: typing.Optional[str], variant: typing.Optional[str] = None
    ) -> typing.Tuple[typing.Optional[str], typing.Dict[str, typing.Any]]:
        """Get implementation string.

        Args:
            lib: Library
            reference: Reference cell
            variant: Variant name

        Raturns:
            Implementation string
        """
        assert self.implemented(lib)
        if variant is None:
            data = self.data["implementations"][lib]
        else:
            if variant not in self.data["implementations"][lib]:
                raise VariantNotImplemented()
            data = self.data["implementations"][lib][variant]
        if isinstance(data, dict):
            if reference not in data:
                return None, {}
            out = data[reference]
        else:
            out = data
        params = {}
        if "=" in out:
            sp = out.split("=")
            out = " ".join(sp[0].split(" ")[:-1])
            sp[-1] += " "
            for i, j in zip(sp[:-1], sp[1:]):
                i = i.split(" ")[-1]
                j = " ".join(j.split(" ")[:-1])
                params[i] = j

        return out, params

    def list_of_implementation_strings(
        self, lib: str, joiner: typing.Union[None, str] = "<br />"
    ) -> typing.Union[str, typing.List[str]]:
        """Get a list of implementation strings.

        Args:
            lib: The library
            joiner: HTML to put between strings, or None if a list is desired

        Returns:
            List of implemtation strings
        """
        assert self.implemented(lib)

        if "display" in self.data["implementations"][lib]:
            d = implementations[lib].format(self.data["implementations"][lib]["display"], {})
            return f"<code>{d}</code>"
        if "variants" in self.data:
            variants = self.data["variants"]
        else:
            variants = {None: {}}

        i_dict: typing.Dict[str, typing.List[str]] = {}
        for v, vinfo in variants.items():
            if v is None:
                data = self.data["implementations"][lib]
            else:
                if v not in self.data["implementations"][lib]:
                    continue
                data = self.data["implementations"][lib][v]
            if isinstance(data, str):
                s = implementations[lib].format(*self.get_implementation_string(lib, None, v))
                if s not in i_dict:
                    i_dict[s] = []
                if v is None:
                    i_dict[s].append("")
                else:
                    i_dict[s].append(vinfo["variant-name"])
            else:
                for i, j in data.items():
                    s = implementations[lib].format(*self.get_implementation_string(lib, i, v))
                    if s not in i_dict:
                        i_dict[s] = []
                    if v is None:
                        i_dict[s].append(i)
                    else:
                        i_dict[s].append(f"{i}, {vinfo['variant-name']}")
        if len(i_dict) == 1:
            return f"<code>{list(i_dict.keys())[0]}</code>"
        imp_list = [f"<code>{i}</code> <span style='font-size:60%'>({'; '.join(j)})</span>"
                    for i, j in i_dict.items()]
        if joiner is None:
            return imp_list
        else:
            return joiner.join(imp_list)

    def make_implementation_examples(self, lib: str) -> str:
        """Make implementation examples for a library.

        Args:
            lib: The library

        Returns:
            Examples
        """
        return implementations[lib].example(self)

    def has_implementation_examples(self, lib: str) -> bool:
        """Check if element has implementation examples for a library.

        Args:
            lib: The library

        Returns:
            True if library has examples, otherwise False
        """
        return lib in examples

    def implementation_notes(self, lib: str) -> typing.List[str]:
        """Get implementation notes for a library.

        Args:
            lib: The library

        Returns:
            Implementation notes
        """
        return implementations[lib].notes(self)

    def implementation_references(self, lib: str) -> typing.List[typing.Dict[str, str]]:
        """Get implementation notes for a library.

        Args:
            lib: The library

        Returns:
            Implementation notes
        """
        return implementations[lib].references(self)

    def categories(self, link: bool = True, map_name: bool = True) -> typing.List[str]:
        """Get categories.

        Args:
            link: Should links be included?
            map_name: Should names be mapped?

        Returns:
            Categories
        """
        assert self._c is not None

        if "categories" not in self.data:
            return []
        if map_name:
            cnames = {c: self._c.get_category_name(c) for c in self.data["categories"]}
        else:
            cnames = {c: c for c in self.data["categories"]}
        if link:
            return [f"<a href='/lists/categories/{c}.html'>{cnames[c]}</a>"
                    for c in self.data["categories"]]
        else:
            return [f"{cnames[c]}" for c in self.data["categories"]]

    def references(self) -> typing.List[str]:
        """Get reference cells.

        Returns:
            reference cells
        """
        assert self._c is not None

        references = self.data["references"] if "references" in self.data else []

        if "complexes" in self.data:
            for key, families in self.data["complexes"].items():
                if not isinstance(families, (list, tuple)):
                    families = [families]
                for e in families:
                    e_s = e.split(",")
                    if len(e_s) == 3:
                        fam, ext, cell = e_s
                        k = "k"
                    else:
                        fam, ext, cell, k = e_s
                    data = self._c.families[key][fam]
                    if "arnold-logg" in data and arnold_logg_reference not in references:
                        references.append(arnold_logg_reference)
                    if "cockburn-fu" in data and cockburn_fu_reference not in references:
                        references.append(cockburn_fu_reference)
                    if "references" in data:
                        for r in references:
                            if r not in references:
                                references.append(r)
        for i in implementations:
            if self.implemented(i):
                for ref in self.implementation_references(i):
                    if ref not in references:
                        references.append(ref)
        return references

    @property
    def test(self) -> bool:
        """Check if element should be tested by default.

        Returns:
            True if it should be tested, otherwise False
        """
        return "test" in self.data

    @property
    def has_examples(self) -> bool:
        """Check if element has examples.

        Returns:
            True if it has examples, otherwise False
        """
        return "examples" in self.data

    @property
    def examples(self) -> typing.List[str]:
        """Get exmaples.

        Returns:
            List of examples
        """
        if "examples" not in self.data:
            return []
        return self.data["examples"]


class Categoriser:
    """Categoriser."""

    def __init__(self):
        """Initialise."""
        self.elements = []
        self.families = {}
        self.references = {}
        self.categories = {}

    def recently_added(self, n: int) -> typing.List[Element]:
        """Get recently added elements.

        Args:
            n: Number of elements

        Returns:
            List of recently added elements
        """
        if self.elements[0].created is None:
            return self.elements[:n]
        return sorted(self.elements, key=lambda e: e.created)[:-n-1:-1]

    def recently_updated(self, n: int) -> typing.List[Element]:
        """Get recently updated elements.

        Args:
            n: Number of elements

        Returns:
            List of recently updated elements
        """
        if self.elements[0].modified is None:
            return self.elements[:n]
        return sorted(self.elements, key=lambda e: e.modified)[:-n-1:-1]

    def load_categories(self, file: str):
        """Load categories from a file.

        Args:
            file: Filename
        """
        with open(file) as f:
            for line in f:
                if line.strip() != "":
                    a, b = line.split(":", 1)
                    self.add_category(a.strip(), b.strip(), f"{a.strip()}.html")

    def load_families(self, file: str):
        """Load families from a file.

        Args:
            file: Filename
        """
        with open(file) as f:
            self.families = yaml.load(f, Loader=yaml.FullLoader)
        for t in self.families:
            for i in self.families[t]:
                self.families[t][i]["elements"] = {}

    def load_references(self, file: str):
        """Load references from a file.

        Args:
            file: Filename
        """
        with open(file) as f:
            for line in f:
                if line.strip() != "":
                    self.add_reference(line.strip(), f"{line.strip()}.html")

    def load_folder(self, folder: str):
        """Load elements from a folder.

        Args:
            folder: Folder name
        """
        for file in os.listdir(folder):
            if file.endswith(".def") and not file.startswith("."):
                with open(os.path.join(folder, file)) as f:
                    data = yaml.load(f, Loader=yaml.FullLoader)

                fname = file[:-4]

                self.add_element(Element(data, fname))

        if settings.github_token is None:
            warnings.warn("Building without GitHub token. Timestamps will not be obtained.")
        else:
            g = Github(settings.github_token)
            repo = g.get_repo("DefElement/defelement.com")
            for e in self.elements:
                commits = repo.get_commits(path=f"elements/{e.filename}.def")
                try:
                    e.created = commits.get_page(-1)[-1].commit.committer.date
                    e.modified = commits.get_page(0)[0].commit.committer.date
                except IndexError:
                    e.created = datetime.utcnow().replace(tzinfo=pytz.utc)
                    e.modified = datetime.utcnow().replace(tzinfo=pytz.utc)

        self.elements.sort(key=lambda x: x.name.lower())

    def add_family(self, t: str, e: str, name: str, fname: str):
        """Add a family.

        Args:
            t: Family name
            e: Element information
            name: Element name
            fname: Filename
        """
        if len(e.split(",")) == 3:
            i, j, k = e.split(",")
        else:
            i, j, k, _ = e.split(",")
        if t not in self.families:
            self.families[t] = {}
            warnings.warn(f"Complex type included in familes data: {t}")
        if i not in self.families[t]:
            warnings.warn(f"Family not included in familes data: {i}")
            self.families[t][i] = {"elements": {}}
        if k not in self.families[t][i]["elements"]:
            self.families[t][i]["elements"][k] = {}
        self.families[t][i]["elements"][k][j] = (name, fname)

    def add_reference(self, e: str, fname: str):
        """Add reference cell.

        Args:
            e: Reference name
            fname: filename
        """
        self.references[e] = fname

    def add_category(self, fname: str, cname: str, html_filename: str):
        """Add a category.

        Args:
            fname: Filename
            cname: Category name
            html_filename: HTML filename to link to
        """
        self.categories[fname] = (cname, html_filename)

    def get_category_name(self, c: str) -> str:
        """Get category name.

        Args:
            c: Category

        Returns:
            Category name
        """
        return self.categories[c][0]

    def get_space_name(self, element: str, link: bool = True) -> str:
        """Get element space name.

        Args:
            element: Element id
            link: Should a link be included?

        Returns:
            Space name, with or without a link to the element page
        """
        for e in self.elements:
            if e.filename == element:
                if link:
                    return e.html_link
                else:
                    return e.html_name
                break
        raise ValueError(f"Could not find space: {element}")

    def get_element(self, ename: str) -> Element:
        """Get an element.

        Args:
            ename: Element id

        Returns:
            The element
        """
        for e in self.elements:
            if e.name == ename:
                return e
        raise ValueError(f"Could not find element: {ename}")

    def add_element(self, e: Element):
        """Add an element.

        Args:
            e: The element
        """
        self.elements.append(e)
        e._c = self
        for r in e.reference_elements(False):
            assert r in self.references

        for j, k in e.complexes(False, False).items():
            for i in k:
                self.add_family(j, i, e.html_name, e.html_filename)

    def elements_in_category(self, c: str) -> typing.List[Element]:
        """Get elements in a category.

        Args:
            c: Category id

        Returns:
            List of elements
        """
        return [e for e in self.elements if c in e.categories(False, False)]

    def elements_in_implementation(self, i: str) -> typing.List[Element]:
        """Get elements in an implementation.

        Args:
            i: Implementation

        Returns:
            List of elements
        """
        return [e for e in self.elements if e.implemented(i)]

    def elements_by_reference(self, r: str) -> typing.List[Element]:
        """Get elements on a reference.

        Args:
            r: Reference

        Returns:
            List of elements
        """
        return [e for e in self.elements if r in e.reference_elements(False)]
