import os
import warnings
import yaml
from datetime import datetime
from github import Github
from . import snippets
from . import settings
from .families import arnold_logg_name, cockburn_fu_name
from .markup import insert_links
from .polyset import make_poly_set, make_extra_info


def make_dof_data(ndofs):
    if isinstance(ndofs, list):
        return "<br /><br />".join([f"\\({i}\\):<br />{make_dof_data(j)}"
                                    for a in ndofs for i, j in a.items()])

    dof_text = []
    for i, j in ndofs.items():
        txt = f"{i}: "
        txt += make_formula(j)
        dof_text.append(txt)

    return "<br />".join(dof_text)


def make_formula(data):
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


class Categoriser:
    def __init__(self):
        self.elements = []
        self.exterior_families = {}
        self.references = {}
        self.categories = {}
        self.implementations = {}

    def recently_added(self, n):
        if self.elements[0].created is None:
            return self.elements[:n]
        return sorted(self.elements, key=lambda e: e.created)[:-n-1:-1]

    def recently_updated(self, n):
        if self.elements[0].modified is None:
            return self.elements[:n]
        return sorted(self.elements, key=lambda e: e.modified)[:-n-1:-1]

    def load_categories(self, file):
        with open(file) as f:
            for line in f:
                if line.strip() != "":
                    a, b = line.split(":", 1)
                    self.add_category(a.strip(), b.strip(), f"{a.strip()}.html")

    def load_implementations(self, file):
        with open(file) as f:
            self.implementations = yaml.load(f, Loader=yaml.FullLoader)

    def load_families(self, file):
        with open(file) as f:
            self.exterior_families = yaml.load(f, Loader=yaml.FullLoader)
        for i in self.exterior_families:
            self.exterior_families[i]["elements"] = {}

    def load_references(self, file):
        with open(file) as f:
            for line in f:
                if line.strip() != "":
                    self.add_reference(line.strip(), f"{line.strip()}.html")

    def load_folder(self, folder):
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
            repo = g.get_repo("mscroggs/defelement.com")
            for e in self.elements:
                commits = repo.get_commits(path=f"elements/{e.filename}.def")
                try:
                    e.created = commits.get_page(-1)[-1].commit.committer.date
                    e.modified = commits.get_page(0)[0].commit.committer.date
                except IndexError:
                    e.created = datetime.now()
                    e.modified = datetime.now()

    def add_exterior_family(self, e, name, fname):
        if len(e.split(",")) == 3:
            i, j, k = e.split(",")
        else:
            i, j, k, _ = e.split(",")
        if i not in self.exterior_families:
            warnings.warn(f"Family not included in familes data: {i}")
            self.exterior_families[i] = {"elements": {}}
        if k not in self.exterior_families[i]["elements"]:
            self.exterior_families[i]["elements"][k] = {}
        self.exterior_families[i]["elements"][k][j] = (name, fname)

    def add_reference(self, e, fname):
        self.references[e] = fname

    def add_category(self, fname, cname, html_filename):
        self.categories[fname] = (cname, html_filename)

    def get_category_name(self, c):
        return self.categories[c][0]

    def get_space_name(self, element, link=True):
        for e in self.elements:
            if e.filename == element:
                if link:
                    return e.html_link
                else:
                    return e.html_name
                break
        raise ValueError(f"Could not find space: {element}")

    def get_element(self, ename):
        for e in self.elements:
            if e.name == ename:
                return e
        raise ValueError(f"Could not find element: {ename}")

    def add_element(self, e):
        self.elements.append(e)
        e._c = self
        for r in e.reference_elements(False):
            assert r in self.references

        for i in e.exterior_calculus_names(False, False):
            self.add_exterior_family(i, e.html_name, e.html_filename)

    def elements_in_category(self, c):
        return [e for e in self.elements if c in e.categories(False, False)]

    def elements_in_implementation(self, i):
        return [e for e in self.elements if e.implemented(i)]

    def elements_by_reference(self, r):
        return [e for e in self.elements if r in e.reference_elements(False)]


class Element:
    def __init__(self, data, fname):
        self.data = data
        self.filename = fname
        self._c = None
        self.created = None
        self.modified = None

    def min_order(self, ref):
        if "min-order" not in self.data:
            return 0
        if isinstance(self.data["min-order"], dict):
            return self.data["min-order"][ref]
        return self.data["min-order"]

    def max_order(self, ref):
        if "max-order" not in self.data:
            return None
        if isinstance(self.data["max-order"], dict):
            return self.data["max-order"][ref]
        return self.data["max-order"]

    def reference_elements(self, link=True):
        if link:
            return [f"<a href='/lists/references/{e}.html'>{e}</a>"
                    for e in self.data["reference elements"]]
        else:
            return self.data["reference elements"]

    def alternative_names(self, include_bracketed=True, include_exterior=True, link=True,
                          strip_cell_name=False, cell=None):
        if "alt-names" not in self.data:
            return []
        if include_bracketed:
            out = [i[1:-1] if i[0] == "(" and i[-1] == ")" else i
                   for i in self.data["alt-names"]]
        else:
            out = [i for i in self.data["alt-names"] if i[0] != "(" or i[-1] != ")"]

        if cell is not None:
            out = [i for i in out if " (" not in i or cell in i]

        if strip_cell_name:
            out = [i.split(" (")[0] for i in out]

        if include_exterior:
            out += self.exterior_calculus_names(link=link)
        return out

    def short_names(self):
        if "short-names" not in self.data:
            return []
        return self.data["short-names"]

    def cockburn_fu_names(self, link=True):
        if "exterior-calculus" not in self.data:
            return []

        out = []
        ec = self.data["exterior-calculus"]
        if not isinstance(ec, (list, tuple)):
            ec = [ec]
        for e in ec:
            names = []
            e_s = e.split(",")
            if len(e_s) == 3:
                fam, ext, cell = e_s
                k = "k"
            else:
                fam, ext, cell, k = e_s
            data = self._c.exterior_families[fam]
            if "cockburn-fu" in data:
                names.append("\\(" + cockburn_fu_name(data["cockburn-fu"], ext, cell, k) + "\\)")
                if link:
                    entry = f"<a class='nou' href='/families/{fam}.html'>"
                entry += " / ".join(names)
                if link:
                    entry += "</a>"
                out.append(entry)
        return out

    def arnold_logg_names(self, link=True):
        if "exterior-calculus" not in self.data:
            return []

        out = []
        ec = self.data["exterior-calculus"]
        if not isinstance(ec, (list, tuple)):
            ec = [ec]
        for e in ec:
            names = []
            e_s = e.split(",")
            if len(e_s) == 3:
                fam, ext, cell = e_s
                k = "k"
            else:
                fam, ext, cell, k = e_s
            data = self._c.exterior_families[fam]
            if "arnold-logg" in data:
                names.append("\\(" + arnold_logg_name(data["arnold-logg"], ext, cell, k) + "\\)")
                if link:
                    entry = f"<a class='nou' href='/families/{fam}.html'>"
                entry += " / ".join(names)
                if link:
                    entry += "</a>"
                out.append(entry)
        return out

    def exterior_calculus_names(self, link=True, math=True):
        if "exterior-calculus" not in self.data:
            return []

        if not math:
            assert not link
            if not isinstance(self.data["exterior-calculus"], (list, tuple)):
                return [self.data["exterior-calculus"]]
            return self.data["exterior-calculus"]

        out = []
        ec = self.data["exterior-calculus"]
        if not isinstance(ec, (list, tuple)):
            ec = [ec]
        for e in ec:
            names = []
            i, j, k = e.split(",")
            data = self._c.exterior_families[i]
            for key, f in [("arnold-logg", arnold_logg_name),
                           ("cockburn-fu", cockburn_fu_name)]:
                if key in data:
                    names.append("\\(" + f(data[key], j, k) + "\\)")
            if link:
                entry = f"<a class='nou' href='/families/{i}.html'>"
            entry += " / ".join(names)
            if link:
                entry += "</a>"
            out.append(entry)
        return out

    def order_range(self):
        def make_order_data(min_o, max_o):
            if isinstance(min_o, dict):
                orders = []
                for i, min_i in min_o.items():
                    if isinstance(max_o, dict) and i in max_o:
                        orders.append(i + ": " + make_order_data(min_i, max_o[i]))
                    else:
                        orders.append(i + ": " + make_order_data(min_i, max_o))
                return "<br />\n".join(orders)
            if max_o is None:
                return f"\\({min_o}\\leqslant k\\)"
            if max_o == min_o:
                return f"\\(k={min_o}\\)"
            return f"\\({min_o}\\leqslant k\\leqslant {max_o}\\)"

        return make_order_data(
            self.data["min-order"] if "min-order" in self.data else 0,
            self.data["max-order"] if "max-order" in self.data else None)

    def sub_elements(self, link=True):
        assert self.is_mixed
        out = []
        for e in self.data["mixed"]:
            element, order = e.split("(")
            order = order.split(")")[0]
            space_link = self._c.get_space_name(element, link=link)
            out.append(f"<li>order \\({order}\\) {space_link} space</li>")
        return out

    def make_dof_descriptions(self):
        if "dofs" not in self.data:
            return ""

        def dofs_on_entity(entity, dofs):
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
                space, order = space_info.split(",")
                space = space.strip()
                order = order.strip()
                space_link = self._c.get_space_name(space)
                return f"{mom_type} with an order \\({order}\\) {space_link} space"
            return dofs

        def make_dof_d(data, post=""):
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

    def make_polynomial_set_html(self):
        # TODO: move some of this to polynomial file
        if "polynomial set" not in self.data:
            return []
        psets = {}
        for i, j in self.data["polynomial set"].items():
            if j not in psets:
                psets[j] = []
            psets[j].append(i)
        if (
            "reference elements" in self.data and len(psets) == 1
            and len(list(psets.values())[0]) == len(self.data["reference elements"])
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

    def dof_counts(self):
        if "ndofs" not in self.data:
            return ""
        return make_dof_data(self.data["ndofs"])

    def entity_dof_counts(self):
        if "entity-ndofs" not in self.data:
            return ""
        return make_dof_data(self.data["entity-ndofs"])

    @property
    def name(self):
        return self.data["name"]

    @property
    def notes(self):
        if "notes" not in self.data:
            return []
        return self.data["notes"]

    @property
    def html_name(self):
        if "html-name" in self.data:
            return self.data["html-name"]
        else:
            return self.data["name"]

    @property
    def html_filename(self):
        return f"{self.filename}.html"

    @property
    def is_mixed(self):
        return "mixed" in self.data

    @property
    def html_link(self):
        return f"<a href='/elements/{self.html_filename}'>{self.html_name}</a>"

    def implemented(self, lib):
        return lib in self.data

    def get_implementation_string(self, lib, reference):
        assert self.implemented(lib)
        if isinstance(self.data[lib], dict):
            if reference not in self.data[lib]:
                return None, {}
            out = self.data[lib][reference]
        else:
            out = self.data[lib]
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

        if " variant=" in out:
            return out.split(" variant=")
        return out, None

    def list_of_implementation_strings(self, lib, joiner="<br />"):
        assert self.implemented(lib)
        if isinstance(self.data[lib], str):
            s, params = self.get_implementation_string(lib, None)
            if lib == "basix":
                s = f"basix.ElementFamily.{s}"
                if "lagrange_variant" in params:
                    s += f", ..., basix.LagrangeVariant.{params['lagrange_variant']}"
            else:
                s = f"\"{s}\""
                if "variant" in params:
                    s += f", variant=\"{params['variant']}\""
            return f"<code>{s}</code>"

        i_dict = {}
        for i, j in self.data[lib].items():
            s, params = self.get_implementation_string(lib, i)
            if lib == "basix":
                s = f"basix.ElementFamily.{s}"
                if "lagrange_variant" in params:
                    s += f", ..., basix.LagrangeVariant.{params['lagrange_variant']}"
            else:
                s = f"\"{s}\""
                if "variant" in params:
                    s += f", variant=\"{params['variant']}\""
            if s not in i_dict:
                i_dict[s] = []
            i_dict[s].append(i)
        imp_list = [f"<code>{i}</code> ({', '.join(j)})" for i, j in i_dict.items()]
        if joiner is None:
            return imp_list
        else:
            return joiner.join(imp_list)

    def make_implementation_examples(self, lib):
        return getattr(snippets, f"{lib}_example")(self)

    def has_implementation_examples(self, lib):
        return hasattr(snippets, f"{lib}_example")

    def categories(self, link=True, map_name=True):
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

    def references(self):
        if "references" not in self.data:
            return []
        return self.data["references"]

    @property
    def test(self):
        return "test" in self.data

    @property
    def has_examples(self):
        return "examples" in self.data

    @property
    def examples(self):
        if "examples" not in self.data:
            return []
        return self.data["examples"]
