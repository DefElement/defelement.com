"""Bempp implementation."""

import typing

from defelement.implementations.template import (Element, Implementation, VariantNotImplemented,
                                                 parse_example)


class BemppImplementation(Implementation):
    """Bempp implementation."""

    @staticmethod
    def format(string: typing.Optional[str], params: typing.Dict[str, typing.Any]) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """
        return f"\"{string}\""

    @staticmethod
    def example(element: Element) -> str:
        """Generate examples.

        Args:
            element: The element

        Returns:
            Example code
        """
        out = "import bempp.api"
        out += "\n"
        out += "grid = bempp.api.shapes.regular_sphere(1)"
        for e in element.examples:
            ref, deg, variant, kwargs = parse_example(e)
            assert len(kwargs) == 0
            deg = int(deg)

            try:
                bempp_name, params = element.get_implementation_string("bempp", ref, variant)
            except VariantNotImplemented:
                continue

            if bempp_name is None:
                continue
            degrees = [int(i) for i in params["degrees"].split(",")]

            if deg in degrees:
                out += "\n\n"
                out += f"# Create {element.name} degree {deg}\n"
                out += "element = bempp.api.function_space(grid, "
                out += f"\"{bempp_name}\", {deg})"
        return out

    id = "bempp"
    name = "Bempp"
    url = "https://github.com/bempp/bempp-cl"
    install = "pip3 install numba scipy meshio\npip3 install bempp-cl"
