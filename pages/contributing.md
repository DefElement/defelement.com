# Contributing to DefElement
You can contribute to DefElement by forking the [DefElement GitHub repo](https://github.com/mscroggs/defelement.com),
making changes, then opening a pull request.

## Defining an element
Elements in the DefElement database are defined using a yaml file in the `elements/` folder.
The full file for a Lagrange element is:

```
name: Lagrange
html-name: Lagrange
alt-names:
  - Polynomial
  - Galerkin
short-names:
  - P
  - CG
  - DG
ndofs:
  interval: k+1
  triangle: (k+1)(k+2)/2
  tetrahedron: (k+1)(k+2)(k+3)/6
ndofs-oeis:
  interval: A000027
  triangle: A000217
  tetrahedron: A000292
categories:
  - scalar
reference elements:
  - interval
  - triangle
  - tetrahedron
dofs:
  vertices: point evaluations
  edges: point evaluations
  faces: point evaluations
  volumes: point evaluations
polynomial set:
  interval: poly[k]
  triangle: poly[k]
  tetrahedron: poly[k]
symfem:
  interval: Lagrange
  triangle: Lagrange
  tetrahedron: Lagrange
examples:
  - interval,1
  - interval,2
  - interval,3
  - triangle,1
  - triangle,2
  - triangle,3
test: 1
```

The entries in this yaml file are:

<table class='bordered align-left'>
<thead>
<tr><td>Name</td><td>Required</td><td>Description</td></tr>
</thead>
<tr><td>`name`</td><td>Yes</td><td>The name of the element (ascii).</td></tr>
<tr><td>`html-name`</td><td>Yes</td><td>The name of the element, including HTML special characters.</td></tr>
<tr><td>`alt-names`</td><td></td><td>Alternative (HTML) names of the element.</td></tr>
<tr><td>`short-names`</td><td></td><td>Abbreviated names of the element.</td></tr>
<tr><td>`ndofs`</td><td></td><td>The number of DOFs the element has.</td></tr>
<tr><td>`ndofs-oeis`</td><td></td><td>A-numbers of the [OEIS](http://oeis.org) sequence(s) giving the number of DOFs.</td></tr>
<tr><td>`categories`</td><td></td><td>Categories the element belongs to. Categories are defined in the file [`/data/categories`](https://github.com/mscroggs/defelement.com/blob/main/data/categories).</td></tr>
<tr><td>`reference&nbsp;elements`</td><td>Yes</td><td>The reference element(s) that this finite element can be defined on.</td></tr>
<tr><td>`dofs`</td><td></td><td>Description of the DOFs of this element.</td></tr>
<tr><td>`polynomial&nbsp;set`</td><td></td><td>The polynomial set of this element. This can use sets defined in the file [`/data/polysets`](https://github.com/mscroggs/defelement.com/blob/main/data/polysets). Other sets can be given by writing `<k>[LaTeX definition of set]`. Unions of multiple sets can be given, separated by ` && `.</td></tr>
<tr><td>`examples`</td><td></td><td>Reference elements and orders to be included in the examples section of the entry.</td></tr>
<tr><td>`symfem`</td><td></td><td>The string used to define this element in [symfem](https://github.com/mscroggs/symfem)'s `create_element` function.</td></tr>
<tr><td>`notes`</td><td></td><td>Notes about the element.</td></tr>
<tr><td>`test`</td><td></td><td>If included, this element's examples will be included when the test version of the website is built. If not, the example will be skipped to speed up the test build.</td></tr>
</table>
