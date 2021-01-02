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
