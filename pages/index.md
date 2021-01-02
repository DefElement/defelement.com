<div style='float:right;width:220px;padding:10px'>
<div>{{plot::triangle,Lagrange,2::1}}</div>
<div style='font-size:80%;color:#AAAAAA;text-align:center'>A basis function of an order 2 [Lagrange space](element::lagrange) on a triangle</div>
<div>{{plot::triangle,Raviart-Thomas,1::1}}</div>
<div style='font-size:80%;color:#AAAAAA;text-align:center'>A basis function of an order 1 [Raviart&ndash;Thomas space](element::raviart-thomas) on a triangle</div>
<div>{{reference::triangle}}</div>
<div style='font-size:80%;color:#AAAAAA;text-align:center'>The reference triangle</div>
</div>

Welcome to DefElement: an encyclopedia of finite element definitions.

This website contains a collection of definitions of finite elements, 
including commonly used elements such as
[Lagrange](element::lagrange) and [Raviart&ndash;Thomas](element::raviart-thomas) elements,
and more exotic elements such as
[serendipity H(div)](element::sdiv) elements.
You can:
<ul>
<li>[view the full alphabetical list of elements](index::all)</li>
<li>[view the elements by category](index::categories)</li>
<li>[view the elements by reference element](index::references)</li>
</ul>

## The finite element method
The finite element method is a numerical method that involves discretising a problem using a finite
dimensional function space. These function spaces are commonly defined using a finite element
on a reference element to derive basis functions for the space. This website contains a collection
of finite elements, and examples of the basis functions they define.

Following the [Ciarlet definition](ciarlet.md) of a finite element, the elements on this website
are defined using a reference element, a polynomial space, and a set of functionals. Each element's
page describes how these are defined for that element, and gives examples of these and the basis
functions they lead to for a selection of low-order spaces.

You can read a detailed description of how the finite element definitions can be understood
[here](ciarlet.md).

## Contributing to DefElement
If you find an error or inaccuracy in a DefElement entry, please open
[an issue on GitHub](https://github.com/mscroggs/defelement.com/issues).
You can also open an issue to suggest a new element that should be added to the database.

Alternatively, you could fork the [DefElement GitHub repo](https://github.com/mscroggs/defelement.com),
make the changes yourself, and open a pull request. You can find more information about adding
an element to DefElement [here](contributing.md).

The functional information and examples on the element pages are generated using
[symfem](https://github.com/mscroggs/symfem), a symbolic finite element definition library.
Before adding an element to DefElement, it should first be implemented in symfem.
