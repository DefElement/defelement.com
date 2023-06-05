import yaml


def parse_metadata(content):
    metadata = {}
    if content.startswith("--\n"):
        metadata, content = content[3:].split("\n--\n", 1)
        metadata = yaml.load(metadata, Loader=yaml.FullLoader)
    return metadata, content.strip()


def insert_author_info(content, authors, url):
    assert content.startswith("# ")
    title, content = content.split("\n", 1)
    return f"{title}\n{{{{author-info::{';'.join(authors)}|{title[1:].strip()}|{url}}}}}\n{content}"
