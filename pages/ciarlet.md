# How to define a finite element
This page describes how finite elements are defined in the DefElement database.

## Cell subentities
Throughout this website, the subentities of a reference element will be referred to as described here.

The vertices, edges, faces, and volumes of a reference element have dimension
0, 1, 2, and 3 (respectively).
The (topological) dimension \(d\) is the dimension of the reference element itself.
(When using the finite element method, the topological dimensions may differ from the
<em>geometric</em> dimension: for example, when meshing a 2D manifold in 3D space, the
topological and geometric dimensions are 2 and 3 (respectively).)

The codimension of an entity is given by subtracting the dimension of the entity from the
topological dimension of the reference element. Entities of codimension 1, 2, and 3 are
called facets, ridges and peaks (respectively). The usual names given to entities of
reference elements of topological dimensions 0 to 3 are shown below.

<center>
<table class='bordered'>
<thead>
<tr><td>Topological dimension</td><td colspan=4>Entities by dimension</td><td colspan=4>Entities by codimension</td></tr>
<tr><td></td><td>0</td><td>1</td><td>2</td><td>3</td><td>0</td><td>1 (facets)</td><td>2 (ridges)</td><td>3 (peaks)</td></td>
</thead>
<tr><td>0 (a vertex)</td><td>point</td><td>-</td><td>-</td><td>-</td><td>the cell</td><td>-</td><td>-</td><td>-</td></tr>
<tr><td>1 (an interval)</td><td>points</td><td>edge</td><td>-</td><td>-</td><td>the cell</td><td>points</td><td>-</td><td>-</td></tr>
<tr><td>2 (a polygon)</td><td>points</td><td>edges</td><td>face</td><td>-</td><td>the cell</td><td>edges</td><td>points</td><td>-</td></tr>
<tr><td>3 (a polyhedron)</td><td>points</td><td>edges</td><td>faces</td><td>volume</td><td>the cell</td><td>faces</td><td>edges</td><td>points</td></tr>
</table>
</center>

## Ciarlet finite elements
The Ciarlet definition <ref type="book" title="The Finite Element Method for Elliptic Problems" author="Ciarlet, P. G." year="1978" publisher="North-Holland">
defines a finite element by a triple \(({{symbols.reference}},{{symbols.polyset}},{{symbols.dual_basis}})\), where

<ul>
<li>\({{symbols.reference}}\subset\mathbb{R}^d\) is the reference element, ususally a polygon or polyhedron;</li>
<li>\({{symbols.polyset}}\) is a finite dimensional polynomial space on \({{symbols.reference}}\) of dimension \(n\);</li>
<li>\({{symbols.dual_basis}}=\{{{symbols.functional}}_0,...,{{symbols.functional}}_{n-1}\}\) is a basis of the dual space \({{symbols.polyset}}^*=\{f:{{symbols.polyset}}\to\mathbb{R}\}\).</li>
</ul>

The basis functions \(\{{{symbols.basis_function}}_0,...,{{symbols.basis_function}}_{n-1}\}\)
of the finite element space are defined by

\[{{symbols.functional}}_i({{symbols.basis_function}}_j) = \begin{cases}1&i=j\\0&i\not=j\end{cases}\]

### Example: Order 1 Lagrange space on a triangle
An order 1 [Lagrange space](element::lagrange) on a triangle is defined by:

<ul>
<li>\({{symbols.reference}}\) is a triangle with vertices at \((0,0)\), \((1,0)\) and \((0,1)\);</li>
<li>\({{symbols.polyset}}=\operatorname{span}\{1, x, y\}\);</li>
<li>\({{symbols.dual_basis}}=\{{{symbols.functional}}_0,{{symbols.functional}}_1,{{symbols.functional}}_2\}\).
</ul>

The functionals \({{symbols.functional}}_1\) to \({{symbols.functional}}_3\) are defined as
point evaluations at the three vertices of the triangle:

\[{{symbols.functional}}_0:v\mapsto v(0,0)\]
\[{{symbols.functional}}_1:v\mapsto v(1,0)\]
\[{{symbols.functional}}_2:v\mapsto v(0,1)\]

It follows from these definitions that the basis functions of the finite element spaces are
linear functions that are equal 1 to at one of the vertices, and equal to 0 at the other two.
These are:

\[{{symbols.basis_function}}_0(x,y)=1-x-y\]
\[{{symbols.basis_function}}_1(x,y)=x\]
\[{{symbols.basis_function}}_2(x,y)=y\]

{{plot::triangle,Lagrange,1}}

## Integral moments
It is common to use integral moment functionals when defining finite elements. Given a mesh
entity \(e\) and a finite element space \((e,{{symbols.polyset}}_e,{{symbols.dual_basis}}_e)\) defined on \(e\),
the integral moment functionals \({{symbols.functional}}_1,...,{{symbols.functional}}_{n_e}\) are defined by
\[{{symbols.functional}}_i:v\mapsto \int_e v{{symbols.basis_function}}_i,\]
where \({{symbols.basis_function}}_1,...,{{symbols.basis_function}}_{n_e}\) are the basis functions of the finite
element space on \(e\).

For vector-values spaces, integral moment functional can be defined using a vector-valued space
on \(e\) and taking the dot product inside the integral,
\[{{symbols.functional}}_i:\mathbf{v}\mapsto \int_e \mathbf{v}\cdot\mathbf{{{symbols.basis_function}}}_i.\]
Alternatively, an integral moment can
be taken with a scalar-valued space by taking the dot product with a fixed vector \(\mathbf{a}\),
\[{{symbols.functional}}_i:\mathbf{v}\mapsto \int_e \mathbf{v}\cdot\mathbf{a}\,{{symbols.basis_function}}_i.\]
Typically, \(\mathbf{a}\) will be tangent to an edge, normal to a facet, or a unit vector in one of
the coordinate directions.

### Example: Order 1 N&eacute;d&eacute;lec (second kind) space on a triangle
The functionals that define an order 1 [N&eacute;d&eacute;lec (second kind) space](element::nedelec2)
on a triangle <ref author="N&eacute;d&eacute;lec, J. C." title="A new family of mixed finite elements in \(\mathbb{R}^3\)" journal="Numerische Mathematik" volume="50" issue="1" year="1986" doi="10.1007/BF01389668" pagestart=57 pageend=81>
are tangential integral moments with order 1 Lagrange spaces on the edges of the triangle.
For example, the two functionals on the edge \(e_0\) of the triangle between \((1,0)\) and \((0,1)\) are
\[{{symbols.functional}}_0=\int_{e_0}\mathbf{v}\cdot\left(\begin{array}{c}-\frac1{\sqrt2}\\\frac1{\sqrt{2}}\end{array}\right)(1-t_0),\]
\[{{symbols.functional}}_1=\int_{e_0}\mathbf{v}\cdot\left(\begin{array}{c}-\frac1{\sqrt2}\\\frac1{\sqrt{2}}\end{array}\right)t_0,\]
where \(t_0\) varies from 0 (at \((1,0)\)) to 1 (at \((0,1)\)) along \(e_0\).

The basis functions of this space are:
{{plot::triangle,N2curl,1}}
