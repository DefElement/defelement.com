"""Basix implementation."""

import typing

from defelement.implementations.core import (Array, Element, Implementation,
                                             VariantNotImplemented, parse_example)


class BasixImplementation(Implementation):
    """Basix implementation."""

    @staticmethod
    def format(string: typing.Optional[str], params: typing.Dict[str, typing.Any]) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """
        out = f"basix.ElementFamily.{string}"
        for p, v in params.items():
            out += f", {p}="
            if p == "lagrange_variant":
                out += f"basix.LagrangeVariant.{v}"
            elif p == "dpc_variant":
                out += f"basix.DPCVariant.{v}"
            elif p == "discontinuous":
                out += v
        return out

    @staticmethod
    def example(element: Element) -> str:
        """Generate examples.

        Args:
            element: The element

        Returns:
            Example code
        """
        out = "import basix"
        for e in element.examples:
            ref, deg, variant, kwargs = parse_example(e)
            assert len(kwargs) == 0

            try:
                basix_name, input_deg, params = element.get_implementation_string(
                    "basix", ref, deg, variant)
            except NotImplementedError:
                continue

            out += "\n\n"
            out += f"# Create {element.name_with_variant(variant)} degree {deg} on a {ref}\n"
            out += "element = basix.create_element("
            out += f"basix.ElementFamily.{basix_name}, basix.CellType.{ref}, {input_deg}"
            if "lagrange_variant" in params:
                out += f", lagrange_variant=basix.LagrangeVariant.{params['lagrange_variant']}"
            if "dpc_variant" in params:
                out += f", dpc_variant=basix.DPCVariant.{params['dpc_variant']}"
            if "discontinuous" in params:
                assert params["discontinuous"] in ["True", "False"]
                out += f", discontinuous={params['discontinuous']}"
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
        import basix

        ref, deg, variant, kwargs = parse_example(example)
        assert len(kwargs) == 0
        basix_name, input_deg, params = element.get_implementation_string("basix", ref, deg, variant)
        kwargs = {}
        if "lagrange_variant" in params:
            kwargs["lagrange_variant"] = getattr(basix.LagrangeVariant, params['lagrange_variant'])
        if "dpc_variant" in params:
            kwargs["dpc_variant"] = getattr(basix.DPCVariant, params['dpc_variant'])
        if "discontinuous" in params:
            kwargs["discontinuous"] = params["discontinuous"] == "True"

        e = basix.create_element(
            getattr(basix.ElementFamily, basix_name), getattr(basix.CellType, ref), input_deg,
            **kwargs)
        return e.entity_dofs, lambda points: e.tabulate(0, points)[0].transpose((0, 2, 1))

    id = "basix"
    name = "Basix"
    url = "https://github.com/FEniCS/basix"
    verification = True
    install = "pip3 install fenics-basix"
