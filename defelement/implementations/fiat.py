"""FIAT implementation."""

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
        if started:
            out += ")"
        return out

    @staticmethod
    def example(element: Element) -> str:
        """Generate Symfem examples.

        Args:
            element: The element

        Returns:
            Example code
        """
        out = "import FIAT"
        for e in element.examples:
            ref, ord, variant, kwargs = parse_example(e)
            assert len(kwargs) == 0
            ord = int(ord)

            try:
                fiat_name, params = element.get_implementation_string("fiat", ref, variant)
            except VariantNotImplemented:
                continue

            if fiat_name is None:
                continue

            if "order" in params and params["order"] != "None" and ord != int(params["order"]):
                continue

            out += "\n\n"
            out += f"# Create {element.name_with_variant(variant)} order {ord}\n"
            if ref in ["interval", "triangle", "tetrahedron"]:
                cell = f"FIAT.ufc_cell(\"{ref}\")"
            elif ref == "quadrilateral":
                cell = "FIAT.reference_element.UFCQuadrilateral()"
            elif ref == "hexahedron":
                cell = "FIAT.reference_element.UFCHexahedron()"
            else:
                raise ValueError(f"Unsupported cell: {ref}")
            out += f"element = FIAT.{fiat_name}({cell}"
            if "order" not in params or params["order"] != "None":
                out += f", {ord}"
            for i, j in params.items():
                if i != "order":
                    out += f", {i}=\"{j}\""
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

        ref, ord, variant, kwargs = parse_example(example)
        assert len(kwargs) == 0
        ord = int(ord)
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

        args = []
        if "order" in params:
            if params["order"] != "None":
                if ord != int(params['order']):
                    raise NotImplementedError
                args.append(ord)
        else:
            args.append(ord)

        e = getattr(FIAT, fiat_name)(
            cell, *args, **{i: j for i, j in params.items() if i != "order"})

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
        return edofs, lambda points: list(e.tabulate(0, points).values())[0].T.reshape(
            points.shape[0], value_size, -1)

    id = "fiat"
    name = "FIAT"
    url = "https://github.com/firedrakeproject/fiat"
    verification = True
    install = "pip3 install git+https://github.com/firedrakeproject/fiat.git"
