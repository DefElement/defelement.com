# Contributing to DefElement

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

### Discussion ideas for new features
You can use [GitHub's Discussions](https://github.com/mscroggs/defelement.com/discussions) to discuss
ideas you have for features (that perhaps aren't fully formed enough yet to make an issue) or to
discuss other people's ideas. You're welcome to also use the Discussions to just chat to other
members of the community.

## Contributing directly

### Submitting a pull request
If you want to directly submit changes to DefElement, you can do this by forking the [DefElement GitHub repository](https://github.com/mscroggs/defelement.com),
making changes, then submitting a pull request.
If you want to contribute, but are unsure where to start, have a look at the
[issue tracker](https://github.com/mscroggs/defelement.com/labels/good%20first%20issue) for issues labelled "good first issue".

The functional information and examples on the element pages are generated using
[Symfem](https://github.com/mscroggs/symfem), a symbolic finite element definition library.
Before adding an element to DefElement, it should first be implemented in Symfem.

### Defining an element
Elements in the DefElement database are defined using a yaml file in the `elements/` folder.
The entries in this yaml file are:

<table class='bordered align-left'>
<thead>
<tr><td>Name</td><td>Required</td><td>Description</td></tr>
</thead>
<tr><td>`name`</td><td>{{tick}}</td><td>The name of the element (ascii).</td></tr>
<tr><td>`html&#8209;name`</td><td>{{tick}}</td><td>The name of the element, including HTML special characters.</td></tr>
<tr><td>`reference&#8209;elements`</td><td>{{tick}}</td><td>The reference element(s) that this finite element can be defined on.</td></tr>
<tr><td>`alt&#8209;names`</td><td></td><td>Alternative (HTML) names of the element.</td></tr>
<tr><td>`short&#8209;names`</td><td></td><td>Abbreviated names of the element.</td></tr>
<tr><td>`variants`</td><td></td><td>Variants of this element.</td></tr>
<tr><td>`complexes`</td><td></td><td>Any discretiations of complexes that this element is part of.</td></tr>
<tr><td>`dofs`</td><td></td><td>Description of the DOFs of this element.</td></tr>
<tr><td>`ndofs`</td><td></td><td>The number of DOFs the element has and the A-numbers of the [OEIS](http://oeis.org) sequence(s) giving the number of DOFs.</td></tr>
<tr><td>`entity&#8209;ndofs`</td><td></td><td>The number of DOFs the element has per subentity type and the A-numbers of the [OEIS](http://oeis.org) sequence(s) giving the number of DOFs.</td></tr>
<tr><td>`polynomial&#8209;set`</td><td></td><td>The polynomial set of this element. This can use sets defined in the file [`/data/polysets`](https://github.com/mscroggs/defelement.com/blob/main/data/polysets). Other sets can be given by writing `<k>[LaTeX definition of set]`. Unions of multiple sets can be given, separated by ` && `.</td></tr>
<tr><td>`mixed`</td><td></td><td>If this element is a mixed element, the subelements that it contains.</td></tr>
<tr><td>`mapping`</td><td></td><td>The mapping used to push/pull values foward/back from/to the reference element.</td></tr>
<tr><td>`sobolev`</td><td></td><td>The Sobolev space the element lives in.</td></tr>
<tr><td>`min&#8209;order`</td><td></td><td>The minimum order of the element</td></tr>
<tr><td>`max&#8209;order`</td><td></td><td>The maximum order of the element</td></tr>
<tr><td>`examples`</td><td></td><td>Reference elements and orders to be included in the examples section of the entry.</td></tr>
<tr><td>`notes`</td><td></td><td>Notes about the element.</td></tr>
<tr><td>`references`</td><td></td><td>References to where the element is defined.</td></tr>
<tr><td>`categories`</td><td></td><td>Categories the element belongs to. Categories are defined in the file [`/data/categories`](https://github.com/mscroggs/defelement.com/blob/main/data/categories).</td></tr>
<tr><td>`basix`</td><td></td><td>The name of the enum item used to define this element in [Basix](https://github.com/fenics/basix)'s `create_element` function.</td></tr>
<tr><td>`basix.ufl`</td><td></td><td>The name of the enum item used to define this element in [Basix.UFL](https://github.com/fenics/basix)'s `element` function.</td></tr>
<tr><td>`bempp`</td><td></td><td>The string used to define this element in [Bempp](https://github.com/bempp/bempp-cl).</td></tr>
<tr><td>`symfem`</td><td></td><td>The string used to define this element in [Symfem](https://github.com/mscroggs/symfem)'s `create_element` function.</td></tr>
<tr><td>`ufl`</td><td></td><td>The string used to define this element in [UFL](https://github.com/fenics/ufl).</td></tr>
<tr><td>`fiat`</td><td></td><td>The class name for this element in [FAIT](https://github.com/firedrakeproject/fiat).</td></tr>
</table>

### Testing your contribution
When you open a pull request, a series of tests and style checks will run via GitHub Actions.
(You may have to wait for manual approval for these to run.)
These tests and checks must pass before the pull request can be merged.
If the tests and checks fail, you can click on them on the pull request page to see where the failure is happening.

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

If you've updated an element, then you can test this element by replacing `auto` with the filename of the element you have edited.
If you've updated multiple elements, you can use multiple filenames separated by commas. For example:

```bash
python3 build.py _test_html --test dpc --processes 4
python3 build.py _test_html --test lagrange,vector-lagrange --processes 4
```

### Adding an implementation
To add a library to the implementations section of DefElement, you must first add details of the
library to the file [`/data/implementations`](https://github.com/mscroggs/defelement.com/blob/main/data/implementations).
You must include three key pieces of information about the library: its `name`, `url`, and a bash command to `install` it.
These three pieces of information are filed under an `id` for your library.

Once this has been done, you should next add the library to [`builder/implementations.py`](https://github.com/mscroggs/defelement.com/blob/main/builder/implementations.py).
At the end of this file, there are three dictionaries, mapping the `id` of a library to a function.
You should add functions to these that do the following:

* The functions in `formats` take an implementation string and a set of parameters as inputs
  and return the implementation information for the library, as it will be displayed on each
  element's page.
* The functions in `examples` take a DefElement `Element` object as an input and return a block
  of Python (as a string) that creates all the examples of that element using the library.
* [optional] The functions in `verifications` take a DefElement `Element` object and an example as
  inputs and return the element for that example tabulated at the set of points given by the
  function `points`. The shape of the output of these functions are
  `(number of points, value size, number of basis functions)`. These functions are used to
  [verify](https://defelement.com/verification.html) that the implementation has the same basis
  functions as Symfem.

Once these steps are done, you can start adding implementation details for your library to
the `implementation` field of elements in the [`elements`](https://github.com/mscroggs/defelement.com/blob/main/elements)
folder.

## Adding yourself to the contributors list
Once you have contributed to DefElement, you should add your name and some information about yourself to the [contributors page](https://defelement.com/contributors.html).
To do this, you should add info about yourself to the file [data/contributors](https://github.com/mscroggs/defelement.com/blob/main/data/contributors). If you wish to include a picture of yourself,
add a square-shaped image to the [pictures/](https://github.com/mscroggs/defelement.com/blob/main/pictures/) folder.

## Code of conduct
We expect all our contributors to follow our [code of conduct](CODE_OF_CONDUCT.md). Any unacceptable
behaviour can be reported to Matthew (defelement@mscroggs.co.uk).
