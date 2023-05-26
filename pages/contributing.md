# Contributing to DefElement

## Suggesting additions and corrections
If you find an error or inaccuracy in a DefElement entry, please open
[an issue on GitHub](https://github.com/mscroggs/defelement.com/issues).
You can also open an issue to suggest a new element that should be added to the database.

## Contributing directly
You can contribute to DefElement by forking the [DefElement GitHub repo](https://github.com/mscroggs/defelement.com),
making changes, then opening a pull request.

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
<tr><td>`bempp`</td><td></td><td>The string used to define this element in [Bempp](https://github.com/bempp/bempp-cl).</td></tr>
<tr><td>`symfem`</td><td></td><td>The string used to define this element in [Symfem](https://github.com/mscroggs/symfem)'s `create_element` function.</td></tr>
<tr><td>`ufl`</td><td></td><td>The string used to define this element in [UFL](https://github.com/fenics/ufl).</td></tr>
</table>

## Adding yourself to the contributors
Once you have contributed to DefElement, you should add your name and some information about
yourself to the [contributors page](contributors.md). To do this, you should add info about
yourself to the file `data/contributors`. If you wish to include a picture of yourself, add
a square-shaped image to the `pictures/` folder.

