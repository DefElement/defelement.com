"""FIAT implementation."""

import sympy
import typing

from defelement.implementations.template import (Array, Element, Implementation,
                                                 VariantNotImplemented, parse_example)


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
            if p == "subdegree":
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
            deg = int(deg)

            try:
                fiat_name, params = element.get_implementation_string("fiat", ref, variant)
            except VariantNotImplemented:
                continue

            if fiat_name is None:
                continue

            if "DEGREEMAP" in params:
                deg = int(sympy.S(params["DEGREEMAP"]).subs(sympy.Symbol("k"), deg))

            if "degree" in params and params["degree"] != "None" and deg != int(params["degree"]):
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
            if "degree" not in params or params["degree"] != "None":
                out += f", {deg}"
            for i, j in params.items():
                if i == "variant":
                    out += f", {i}=\"{j}\""
                if i == "subdegree":
                    out += f", {i}={sympy.S(j).subs(sympy.Symbol('k'), deg)}"
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
        deg = int(deg)
        try:
            fiat_name, params = element.get_implementation_string("fiat", ref, variant)
        except VariantNotImplemented:
            raise NotImplementedError()
        if fiat_name is None:
            raise NotImplementedError()
        if ref in ["interval", "triangle", "tetrahedron"]:
            cell = FIAT.ufc_cell(ref)
        elif ref == "quadrilateral":
            cell = FIAT.reference_element.UFCQuadrilateral()
        elif ref == "hexahedron":
            cell = FIAT.reference_element.UFCHexahedron()
        else:
            raise ValueError(f"Unsupported cell: {ref}")

        if "DEGREEMAP" in params:
            input_deg = int(sympy.S(params["DEGREEMAP"]).subs(sympy.Symbol("k"), deg))
        else:
            input_deg = deg

        args = []
        kwargs = {}
        if "degree" in params and params["degree"] != "None" and deg != int(params['degree']):
            raise NotImplementedError

        args.append(input_deg)
        if "subdegree" in params:
            kwargs["subdegree"] = int(sympy.S(params["subdegree"]).subs(sympy.Symbol('k'), deg))

        if "variant" in params:
            kwargs["variant"] = params["variant"]

        # TODO: remove this once https://github.com/firedrakeproject/fiat/issues/87 is resolved
        if element.name == "Guzman-Neilan (first kind)" and example == "tetrahedron,2":
            raise NotImplementedError()

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

        if element.name == "Arnold-Winther" and example.startswith("triangle"):
            edofs[2][0] = edofs[2][0][:3]
            return edofs, lambda points: list(e.tabulate(0, points).values())[0].T.reshape(
                points.shape[0], value_size, -1)[:, :, :24]
        if element.name == "nonconforming Arnold-Winther" and example.startswith("triangle"):
            for i in range(3):
                edofs[1][i] = edofs[1][i][:4]
            return edofs, lambda points: list(e.tabulate(0, points).values())[0].T.reshape(
                points.shape[0], value_size, -1)[:, :, :15]
        if element.name == "Bell" and example.startswith("triangle"):
            for i in range(3):
                edofs[1][i] = []
            return edofs, lambda points: list(e.tabulate(0, points).values())[0].T.reshape(
                points.shape[0], value_size, -1)[:, :, :18]
        if element.name == "Mardal-Tai-Winther" and example.startswith("triangle"):
            for i in range(3):
                edofs[1][i] = edofs[1][i][:3]
            edofs[2][0] = []
            return edofs, lambda points: list(e.tabulate(0, points).values())[0].T.reshape(
                points.shape[0], value_size, -1)[:, :, :9]
        if element.name == "reduced Hsieh-Clough-Tocher" and example.startswith("triangle"):
            for i in range(3):
                edofs[1][i] = []
            return edofs, lambda points: list(e.tabulate(0, points).values())[0].T.reshape(
                points.shape[0], value_size, -1)[:, :, :9]
        if element.name == "nonconforming Arnold-Winther" and example.startswith("triangle"):
            for i in range(3):
                edofs[1][i] = edofs[1][i][:4]
            return edofs, lambda points: list(e.tabulate(0, points).values())[0].T.reshape(
                points.shape[0], value_size, -1)[:, :, :15]
        if element.name == "Guzman-Neilan (first kind)":
            raise NotImplementedError()

            if example == "triangle,1":
                for i in range(3):
                    edofs[1][i] = edofs[1][i][:1]
                return edofs, lambda points: list(e.tabulate(0, points).values())[0].T.reshape(
                    points.shape[0], value_size, -1)[:, :, :9]
            if example == "tetrahedron,1":
                for i in range(4):
                    edofs[2][i] = edofs[2][i][:1]
                return edofs, lambda points: list(e.tabulate(0, points).values())[0].T.reshape(
                    points.shape[0], value_size, -1)[:, :, :15]

            print(edofs)

        return edofs, lambda points: list(e.tabulate(0, points).values())[0].T.reshape(
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
        if element.name in ["Arnold-Winther", "Bell"]:
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
        if element.name in ["Arnold-Winther", "Bell"]:
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
