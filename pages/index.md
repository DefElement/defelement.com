<div style='float:right;width:220px;padding:10px'>
<div>{{reference::triangle}}</div>
<div style='font-size:80%;color:#AAAAAA;text-align:center'>The reference triangle</div>
<div>{{plot::triangle,Lagrange,2::1}}</div>
<div style='font-size:80%;color:#AAAAAA;text-align:center'>A basis function of an order 2 [Lagrange space](element::lagrange) on a triangle</div>
<div>{{plot::triangle,Raviart-Thomas,1::1}}</div>
<div style='font-size:80%;color:#AAAAAA;text-align:center'>A basis function of an order 1 [Raviart&ndash;Thomas space](element::raviart-thomas) on a triangle</div>
</div>

# Hello there!

Welcome to DefElement: an encyclopedia of finite element definitions.

The finite element method is a numerical method that involves discretising a problem using a finite
dimensional function space. These function spaces are commonly defined using a finite element
on a reference element to derive basis functions for the space. This website contains a collection
of finite elements, and examples of the basis functions they define.

Following the [Ciarlet definition](ciarlet.md) of a finite element, the elements on this website
are defined using a reference element, a polynomial space, and a set of functionals. Each element's
page describes how these are defined for that element, and gives examples of these and the basis
functions they lead to for a selection of low-order spaces.

The elements included on this website include commonly used elements such as [Lagrange](element:lagrange)
and [Raviart&ndash;Thomas](raviart-thomas) elements.
You can [view the full alphabetical list of elements](index::all),
[view the elements by category](index::categories)
or
[view the elements by reference element](index::references).

You can read a detailed description of how the finite element definitions can be understood
[here](ciarlet.md).
