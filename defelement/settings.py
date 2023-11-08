"""DefElement settings."""

import os as _os

dir_path = _os.path.join(_os.path.dirname(_os.path.realpath(__file__)), "..")
element_path = _os.path.join(dir_path, "elements")
template_path = _os.path.join(dir_path, "templates")
files_path = _os.path.join(dir_path, "files")
pages_path = _os.path.join(dir_path, "pages")
data_path = _os.path.join(dir_path, "data")
img_path = _os.path.join(dir_path, "img")

html_path = _os.path.join(dir_path, "_html")
htmlelement_path = _os.path.join(html_path, "elements")
htmlimg_path = _os.path.join(html_path, "img")
htmlindices_path = _os.path.join(html_path, "lists")
htmlfamilies_path = _os.path.join(html_path, "families")

verification_json = _os.path.join(dir_path, "verification.json")

github_token = None

processes = 1
