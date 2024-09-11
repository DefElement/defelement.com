"""Implementation class."""

import re
import typing
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from numpy import float64
    from numpy.typing import NDArray

    from defelement.element import Element
    Array = NDArray[float64]
else:
    Array = typing.Any
    Element = typing.Any


class Implementation(ABC):
    """An implementation."""

    @abstractmethod
    def format(string: typing.Optional[str], params: typing.Dict[str, typing.Any]) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """

    @abstractmethod
    def example(element: Element) -> str:
        """Generate Symfem examples.

        Args:
            element: The element

        Returns:
            Example code
        """

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
        raise NotImplementedError()

    name = None
    verification = False


class VariantNotImplemented(BaseException):
    """Error for variants that are not implemented."""


ValueType = typing.Union[int, str, typing.List["ValueType"]]


def _parse_value(v: str) -> ValueType:
    """Parse a string.

    Args:
        v: String

    Returns:
        Parsed string
    """
    v = v.strip()
    if v[0] == "[" and v[-1] == "]":
        return [_parse_value(i) for i in v[1:-1].split(";")]
    if re.match(r"[0-9]+$", v):
        return int(v)
    return v


def parse_example(
    e: str
) -> typing.Tuple[
    str, int, typing.Optional[str],
    typing.Dict[str, typing.Union[int, str, typing.List[ValueType]]]
]:
    """Parse an example.

    Args:
        e: The example

    Returns:
        Parsed example information
    """
    if " {" in e:
        e, rest = e.split(" {")
        rest = rest.split("}")[0]
        while re.search(r"\[([^\]]*),", rest):
            rest = re.sub(r"\[([^\]]*),", r"[\1;", rest)
        kwargs = {}
        for i in rest.split(","):
            key, value = i.split("=")
            kwargs[key] = _parse_value(value)
    else:
        kwargs = {}
    s = e.split(",")
    if len(s) == 3:
        ref, order, variant = s
    else:
        ref, order = e.split(",")
        variant = None
    return ref, int(order), variant, kwargs
