"""DefElement tools."""

import typing

import yaml

from defelement import settings

if typing.TYPE_CHECKING:
    from numpy import float64
    from numpy.typing import NDArray
    Array = NDArray[float64]
else:
    Array = typing.Any


def parse_metadata(content: str) -> typing.Tuple[typing.Dict[str, typing.Any], str]:
    """Parse metadata.

    Args:
        content: Raw data

    Returns:
        Parsed metadata and content without metadata
    """
    from defelement.markup import preprocess

    metadata: typing.Dict[str, typing.Any] = {"title": None}
    if content.startswith("--\n"):
        metadata_in, content = content[3:].split("\n--\n", 1)
        metadata.update(yaml.load(metadata_in, Loader=yaml.FullLoader))
    content = preprocess(content.strip())
    if metadata["title"] is None and content.startswith("# "):
        metadata["title"] = content[2:].split("\n", 1)[0].strip()
    return metadata, content


def insert_author_info(content: str, authors: typing.List[str], url: str) -> str:
    """Insert author info into content.

    Args:
        content: The content
        authors: List of authors
        url: A URL

    Returns:
        Content with authrso inserted
    """
    assert content.startswith("# ")
    title, content = content.split("\n", 1)
    return f"{title}\n{{{{author-info::{';'.join(authors)}|{title[1:].strip()}|{url}}}}}\n{content}"


def html_local(path: str) -> str:
    """Get the local HTML path of a absolute path.

    Args:
        path: The absolute path

    Returns:
        Local HTML path
    """
    assert path.startswith(settings.html_path)
    return path[len(settings.html_path):]


def to_array(
    data: typing.Union[Array, typing.List[typing.Any], typing.Tuple[typing.Any, ...]]
) -> typing.Union[float, Array]:
    """Convert to an array."""
    import numpy as np

    if isinstance(data, (list, tuple)):
        return np.array([to_array(i) for i in data])
    return float(data)


def comma_and_join(ls: typing.List[str], oxford_comma: bool = True) -> str:
    """Join a list with commas and an and between the last two items."""
    if len(ls) == 1:
        return ls[0]
    if len(ls) == 2:
        return f"{ls[0]} and {ls[1]}"
    return ", ".join(ls[:-1]) + ("," if oxford_comma else "") + " and " + ls[-1]
