"""NDElement implementation."""

import typing

from defelement.implementations.template import (Array, Element, Implementation,
                                                 VariantNotImplemented, parse_example)


class NDElementImplementation(Implementation):
    """NDElement implementation."""

    @staticmethod
    def format(string: typing.Optional[str], params: typing.Dict[str, typing.Any]) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """
        out = f"Family.{string}"
        for p, v in params.items():
            out += f", {p}="
            if p == "continuity":
                out += f"Continuity.{v}"
        return out

    @staticmethod
    def example(element: Element) -> str:
        """Generate examples.

        Args:
            element: The element

        Returns:
            Example code
        """
        out = "\nfrom ndelement.reference_cell import ReferenceCellType"
        cont = False
        for e in element.examples:
            ref, ord, variant, kwargs = parse_example(e)
            assert len(kwargs) == 0
            ord = int(ord)

            try:
                name, params = element.get_implementation_string("ndelement", ref, variant)
            except VariantNotImplemented:
                continue

            if name == "RaviartThomas" and ord > 1:
                continue

            if name is not None:
                out += "\n\n"
                out += f"# Create {element.name_with_variant(variant)} order {ord} on a {ref}\n"
                out += "family = create_family("
                out += f"Family.{name}, {ord}"
                if "continuity" in params:
                    cont = True
                    assert params["continuity"] in ["Standard", "Discontinuous"]
                    out += f", continuity=Continuity.{params['continuty']}"
                out += ")\n"
                out += f"element = family.element(ReferenceCellType.{ref[0].upper() + ref[1:]})"
        if cont:
            out = "from ndelement.ciarlet import Continuity, Family, create_family" + out
        else:
            out = "from ndelement.ciarlet import Family, create_family" + out
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
        from ndelement.ciarlet import Continuity, Family, create_family
        from ndelement.reference_cell import ReferenceCellType, entity_counts

        ref, ord, variant, kwargs = parse_example(example)
        assert len(kwargs) == 0
        ord = int(ord)
        try:
            name, params = element.get_implementation_string("ndelement", ref, variant)
        except VariantNotImplemented:
            raise NotImplementedError()
        if name is None:
            raise NotImplementedError()
        kwargs = {}
        if "continuity" in params:
            kwargs["continuity"] = getattr(Continuity, params["continuity"])
        if "orders" in params:
            if ord not in [int(i) for i in params["orders"].split(",")]:
                raise NotImplementedError()

        cell = getattr(ReferenceCellType, ref[0].upper() + ref[1:])
        e = create_family(getattr(Family, name), ord, **kwargs).element(cell)
        entity_dofs = [[e.entity_dofs(dim, entity) for entity in range(n)]
                       for dim, n in enumerate(entity_counts(cell)) if n > 0]

        return entity_dofs, lambda points: e.tabulate(points, 0)[:, :, :, 0].transpose((2, 0, 1))

    id = "ndelement"
    name = "NDElement"
    url = "https://github.com/bempp/ndelement"
    verification = True
    install = "pip3 install ndelement"
