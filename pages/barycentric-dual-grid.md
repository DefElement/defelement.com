--
authors:
  - Scroggs, Matthew W.
--

# Barycentric dual grids

Some elements are defined on a [barycentric dual grid](reference::dual polygon).
This grid is defined by taking a mesh of triangles:

{{img::mesh-bary0}}

Lines are then added connecting every vertex of each triangle to the midpoint of the opposite
edge:

{{img::mesh-bary1}}

The cells in the dual grid are then defined as the union of all the triangles adjacent to 
one of the vertices in the original mesh:

{{img::mesh-bary2}}

{{img::mesh-bary3}}

In DefElement, regular polygons centred at the origin are used as reference elements of the
dual grid.
