"""Legacy UFL implementation."""

import typing

from defelement.implementations.template import (Element, Implementation, VariantNotImplemented,
                                                 parse_example)


class UFLImplementation(Implementation):
    """UFL implementation."""

    def format(string: typing.Optional[str], params: typing.Dict[str, typing.Any]) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """
        return f"\"{string}\""

    def example(element: Element) -> str:
        """Generate Symfem examples.

        Args:
            element: The element

        Returns:
            Example code
        """
        out = "import ufl_legacy"
        for e in element.examples:
            ref, ord, variant, kwargs = parse_example(e)
            assert len(kwargs) == 0
            ord = int(ord)

            try:
                ufl_name, params = element.get_implementation_string("ufl", ref, variant)
            except VariantNotImplemented:
                continue

            if ufl_name is not None:
                out += "\n\n"
                out += f"# Create {element.name_with_variant(variant)} order {ord} on a {ref}\n"
                if "type" in params:
                    out += f"element = ufl_legacy.{params['type']}("
                else:
                    out += "element = ufl_legacy.FiniteElement("
                out += f"\"{ufl_name}\", \"{ref}\", {ord})"
        return out

    name = "ufl"
