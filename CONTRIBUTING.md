# How to contribute

## Making suggestions

### Reporting mistakes
If you find a mistake in the DefElement database, please report it on the
[issue tracker](https://github.com/mscroggs/defelement.com/issues/new?assignees=&labels=bug&template=mistake-report.md&title=)
using the *Mistake report* template.

### Suggesting new elements
If you want to suggest a new element to be added to DefElement, suggest it on the
[issue tracker](https://github.com/mscroggs/defelement.com/issues/new?assignees=&labels=new+element&template=new-element.md&title=Add+%5BNAME%5D+element)
using the *New element* template.

### Suggesting improvements
If you want to suggest a new featute or improvement to DefElement, suggest it on the
[issue tracker](https://github.com/mscroggs/defelement.com/issues/new?assignees=&labels=feature+request&template=suggest-an-improvement.md&title=)
using the *Suggest an improvement* template.

## Contribution directly

### Submitting a pull request
If you want to directly submit changes to DefElement, you can do this by forking the DefElement repo, then submitting a pull request.
If you want to contribute, but are unsure where to start, have a look at the
[issue tracker](https://github.com/mscroggs/defelement.com/labels/good%20first%20issue) for issues labelled "good first issue".

Information about adding an element of DefElement can be found at
[defelement.com/contributing.html](https://defelement.com/contributing.html).

On opening a pull request, unit tests and style checks will run. You can click on these in the pull request
to see where (if anywhere) there are errors in your changes.

### Testing your contribution
When you open a pull request, a series of tests and style checks will run via GitHub Actions.
(You may have to wait for manual approval for these to run.)
These tests and checks must pass before the pull request can be merged.

The style checks will check that the Python scripts that generate DefElement pass flake8 checks.
If you've changed these scripts, you can run these checks locally by running:

```bash
python3 -m flake8 builder build.py test
```

Before you can run the tests or do a test build, you'll need to install DefElement's requirements:

```bash
python3 -m pip install -r requirements.txt
```

The DefElement tests can be run using:

```bash
python3 -m pytest test/
```

To test that DefElement successfully builds, you can pass `--test auto` to the `build.py` script.
This will build the website including examples for a small set of elements, and will take much less time
then building the full website.

```bash
python3 build.py _test_html --test auto --processes 4
```

## Adding yourself to the contributors list
Once you have contributed to DefElement, you should add your name and some information about yourself to the [contributors page](https://defelement.com/contributors.html).
To do this, you should add info about yourself to the file [data/contributors](data/contributors). If you wish to include a picture of yourself,
add a square-shaped image to the [pictures/](pictures/) folder. 

## Code of conduct
We expect all our contributors to follow [the Contributor Covenant](CODE_OF_CONDUCT.md). Any unacceptable
behaviour can be reported to Matthew (defelement@mscroggs.co.uk).
