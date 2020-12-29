# Ciarlet finite elements
The Ciarlet definition <ref type="book" title="The Finite Element Method for Elliptic Problems" author="Ciarlet, P. G." year="1978" publisher="North-Holland">
defines a finite element by a triple \(({{symbols.reference}},{{symbols.polyset}},{{symbols.dual_basis}})\), where

<ul>
<li>\({{symbols.reference}}\subset\mathbb{R}^d\) is the reference element, ususally a polygon or polyhedron;</li>
<li>\({{symbols.polyset}}\) is a finite dimensional polynomial space on \({{symbols.reference}}\) of dimension \(n\);</li>
<li>\({{symbols.dual_basis}}=\{{{symbols.functional}}_1,...,{{symbols.functional}}_n\}\) is a basis of the dual space \({{symbols.polyset}}^*=\{f:{{symbols.polyset}}\to\mathbb{R}\}\).</li>
</ul>

The basis functions \(\{{{symbols.basis_function}}_1,...,{{symbols.basis_function}}_n\}\)
of the finite element space are defined by

\[{{symbols.functional}}_i({{symbols.basis_function}}_j) = \begin{cases}1&i=j\\0&i\not=j\end{cases}\]

## Example: Order 1 Lagrange space on a triangle

An order 1 [Lagrange space](element::lagrange) on a triangle is defined by:

<ul>
<li>\({{symbols.reference}}\) is a triangle with vertices at \((0,0)\), \((1,0)\) and \((0,1)\);</li>
<li>\({{symbols.polyset}}=\operatorname{span}\{1, x, y\}\);</li>
<li>\({{symbols.dual_basis}}=\{{{symbols.functional}}_1,{{symbols.functional}}_2,{{symbols.functional}}_3\}\).
</ul>

The functionals \({{symbols.functional}}_1\) to \({{symbols.functional}}_3\) are defined as
point evaluations at the three vertices of the triangle:

\[{{symbols.functional}}_1:v\mapsto v(0,0)\]
\[{{symbols.functional}}_2:v\mapsto v(1,0)\]
\[{{symbols.functional}}_3:v\mapsto v(0,1)\]

It follows from these definitions that the basis functions of the finite element spaces are
linear functions that are equal 1 to at one of the vertices, and equal to 0 at the other two.
These are:

\[{{symbols.basis_function}}_1(x,y)=1-x-y\]
\[{{symbols.basis_function}}_2(x,y)=x\]
\[{{symbols.basis_function}}_3(x,y)=y\]

{{plot::triangle,Lagrange,1}}

