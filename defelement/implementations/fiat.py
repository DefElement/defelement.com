"""FIAT implementation."""

import typing

import sympy

from defelement.implementations.core import Array, Element, Implementation, parse_example

# TODO make this a FIAT attribute
true_space_dimension = {
    "Bell": 18,
    "Mardal-Tai-Winther": 9,
    "reduced Hsieh-Clough-Tocher": 9,
    "Arnold-Winther": 24,
    "nonconforming Arnold-Winther": 15,
}


class FIATImplementation(Implementation):
    """FIAT implementation."""

    @staticmethod
    def format(string: typing.Optional[str], params: typing.Dict[str, typing.Any]) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """
        out = f"FIAT.{string}"
        started = False
        for p, v in params.items():
            if p == "variant":
                if not started:
                    out += "(..."
                    started = True
                out += f", {p}=\"{v}\""
            if p in ["subdegree", "reduced"]:
                if not started:
                    out += "(..."
                    started = True
                out += f", {p}={v}"
        if started:
            out += ")"
        return out

    @staticmethod
    def example(element: Element) -> str:
        """Generate examples.

        Args:
            element: The element

        Returns:
                Example code
        """
        out = "import FIAT"
        for e in element.examples:
            ref, deg, variant, kwargs = parse_example(e)
            assert len(kwargs) == 0

            try:
                fiat_name, input_deg, params = element.get_implementation_string(
                    "fiat", ref, deg, variant)
            except NotImplementedError:
                continue

            out += "\n\n"
            out += f"# Create {element.name_with_variant(variant)} degree {deg}\n"
            if ref in ["interval", "triangle", "tetrahedron"]:
                cell = f"FIAT.ufc_cell(\"{ref}\")"
            elif ref == "quadrilateral":
                cell = "FIAT.reference_element.UFCQuadrilateral()"
            elif ref == "hexahedron":
                cell = "FIAT.reference_element.UFCHexahedron()"
            else:
                raise ValueError(f"Unsupported cell: {ref}")
            out += f"element = FIAT.{fiat_name}({cell}"
            if input_deg is not None:
                out += f", {input_deg}"
            for i, j in params.items():
                if i == "variant":
                    out += f", {i}=\"{j}\""
                if i == "subdegree":
                    out += f", {i}={sympy.S(j).subs(sympy.Symbol('k'), deg)}"
                if i == "reduced":
                    out += f", {i}={j}"
            out += ")"
        return out

    @staticmethod
    def verify(
        element: Element, example: str
    ) -> typing.Tuple[typing.List[typing.List[typing.List[int]]], typing.Callable[[Array], Array]]:
        """Get verification data.

        Args:
            element: Element data
            example: Example data

        Returns:
            List of entity dofs, and tabulation function
        """
        import FIAT

        ref, deg, variant, kwargs = parse_example(example)
        assert len(kwargs) == 0

        fiat_name, input_deg, params = element.get_implementation_string("fiat", ref, deg, variant)

        if ref in ["interval", "triangle", "tetrahedron"]:
            cell = FIAT.ufc_cell(ref)
        elif ref == "quadrilateral":
            cell = FIAT.reference_element.UFCQuadrilateral()
        elif ref == "hexahedron":
            cell = FIAT.reference_element.UFCHexahedron()
        else:
            raise ValueError(f"Unsupported cell: {ref}")

        args = []
        kwargs = {}

        if input_deg is not None:
            args.append(input_deg)

        if "variant" in params:
            kwargs["variant"] = params["variant"]

        if "reduced" in params:
            kwargs["reduced"] = bool(params["reduced"])

        e = getattr(FIAT, fiat_name)(cell, *args, **kwargs)

        value_size = 1
        for i in e.value_shape():
            value_size *= i
        edofs = [list(i.values()) for i in e.entity_dofs().values()]
        if ref == "quadrilateral":
            edofs = [
                [edofs[0][0], edofs[0][2], edofs[0][1], edofs[0][3]],
                [edofs[1][2], edofs[1][0], edofs[1][1], edofs[1][3]],
                [edofs[2][0]],
            ]
        if ref == "hexahedron":
            edofs = [
                [edofs[0][0], edofs[0][4], edofs[0][2], edofs[0][6],
                 edofs[0][1], edofs[0][5], edofs[0][3], edofs[0][7]],
                [edofs[1][8], edofs[1][4], edofs[1][0], edofs[1][6], edofs[1][2], edofs[1][10],
                 edofs[1][1], edofs[1][3], edofs[1][9], edofs[1][5], edofs[1][7], edofs[1][11]],
                [edofs[2][4], edofs[2][2], edofs[2][0], edofs[2][1], edofs[2][3], edofs[2][5]],
                [edofs[3][0]],
            ]

        sd = cell.get_spatial_dimension()
        if element.name in {"Bernardi-Raugel",
                            "Guzman-Neilan (first kind)",
                            "Guzman-Neilan (second kind)"}:
            reduced_dim = e.space_dimension() - (sd+1) * (sd-1)
        else:
            reduced_dim = true_space_dimension.get(element.name)

        if reduced_dim is not None:
            for dim in range(len(edofs)):
                for i in range(len(edofs[dim])):
                    edofs[dim][i] = [dof for dof in edofs[dim][i] if dof < reduced_dim]

        z = (0,) * sd
        return edofs, lambda points: e.tabulate(0, points)[z][slice(reduced_dim)].T.reshape(
                points.shape[0], value_size, -1)

    @staticmethod
    def notes(
        element: Element
    ) -> typing.List[str]:
        """Return a list of notes to include for the implementation of this element.

        Args:
            element: Element data

        Returns:
            List of notes
        """
        if element.name in true_space_dimension:
            return ["This implementation includes additional DOFs that are used then filtered "
                    "out when mapping the element, as described in Kirby (2018)."]
        return []

    @staticmethod
    def references(
        element: Element
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """Return a list of additional references to include for the implementation of this element.

        Args:
            element: Element data

        Returns:
            List of references
        """
        if element.name in true_space_dimension:
            return [{
                'title': 'A general approach to transforming finite elements',
                'author': ['Kirby, Robert C.'],
                'year': 2018,
                'journal': 'SMAI Journal of Computational Mathematics',
                'volume': 4,
                'pagestart': 197,
                'pageend': 224,
                'doi': '10.5802/smai-jcm.33',
            }]
        return []

    id = "fiat"
    name = "FIAT"
    url = "https://github.com/firedrakeproject/fiat"
    verification = True
    install = "pip3 install git+https://github.com/firedrakeproject/fiat.git"
