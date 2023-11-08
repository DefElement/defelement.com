import yaml

from . import settings
from .markup import preprocess


def parse_metadata(content):
    metadata = {"title": None}
    if content.startswith("--\n"):
        metadata_in, content = content[3:].split("\n--\n", 1)
        metadata.update(yaml.load(metadata_in, Loader=yaml.FullLoader))
    content = preprocess(content.strip())
    if metadata["title"] is None and content.startswith("# "):
        metadata["title"] = content[2:].split("\n", 1)[0].strip()
    return metadata, content


def insert_author_info(content, authors, url):
    assert content.startswith("# ")
    title, content = content.split("\n", 1)
    return f"{title}\n{{{{author-info::{';'.join(authors)}|{title[1:].strip()}|{url}}}}}\n{content}"


def html_local(path):
    assert path.startswith(settings.html_path)
    return path[len(settings.html_path):]
