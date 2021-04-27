from symfem.core.calculus import grad
from symfem.core.vectors import vdot, vsub
from symfem.core.symbolic import subs, x
from symfem.core.symbolic import PiecewiseFunction

COLORS = {"orange": "#FF8800", "blue": "#44AAFF", "green": "#55FF00",
          "purple": "#DD2299", "light blue": "#BBEEFF",
          "gray": "#AAAAAA"}
ENTITY_COLORS = [COLORS["orange"], COLORS["blue"], COLORS["green"], COLORS["purple"]]


class NoPlot:
    def to_svg(self):
        return ""


class Plot:
    def __init__(self, padding=15, dim=None):
        self.dim = dim
        self.padding = padding
        self.height = 2 * self.padding
        self.width = 2 * self.padding
        self.origin = [self.padding, self.padding]
        self._items = []
        self._zadd = 0.00001

    def map_to_2d(self, point):
        if self.dim is not None:
            point = tuple(point)
            while len(point) < self.dim:
                point += (0, )

        if len(point) == 3 and self.origin[1] == self.padding:
            self.origin[1] += self.padding
            self.height += self.padding
        if len(point) == 0:
            return (self.origin[0], self.origin[1]), 0
        if len(point) == 1:
            return (self.origin[0] + point[0], self.origin[1]), 0
        if len(point) == 2:
            return (self.origin[0] + point[0], self.origin[1] + point[1]), 0
        if len(point) == 3:
            return (
                float(self.origin[0] + point[0] + point[1] / 2),
                float(self.origin[1] + point[2] - 2 * point[0] / 25 + point[1] / 5)
            ), float(point[0] - 2 * point[1] + 12 * point[2] / 25)

    def _add_line(self, start, end, z, color, width):
        line = {"type": "line",
                "z-value": z,
                "start": start,
                "end": end,
                "width": width,
                "color": color}
        self._items.append(line)
        self.width = max(self.width, line["start"][0] + self.padding, line["end"][0] + self.padding)
        self.height = max(self.height, line["start"][1] + self.padding,
                          line["end"][1] + self.padding)

    def add_line(self, start, end, color="black", width="3px"):
        start, z1 = self.map_to_2d(start)
        end, z2 = self.map_to_2d(end)
        self._add_line(start, end, min(z1, z2), color, width)

    def add_bezier(self, start, mid1, mid2, end, color="black", width="3px"):
        start, z1 = self.map_to_2d(start)
        mid1, _ = self.map_to_2d(mid1)
        mid2, _ = self.map_to_2d(mid2)
        end, z2 = self.map_to_2d(end)
        bez = {"type": "bezier",
               "z-value": min(z1, z2),
               "start": start,
               "mid1": mid1,
               "mid2": mid2,
               "end": end,
               "width": width,
               "color": color}
        self._items.append(bez)
        self.width = max(self.width, bez["start"][0] + self.padding, bez["end"][0] + self.padding)
        self.height = max(self.height, bez["start"][1] + self.padding,
                          bez["end"][1] + self.padding)

    def add_arrow(self, start, end, color="black", width="3px"):
        start, z1 = self.map_to_2d(start)
        end, z2 = self.map_to_2d(end)
        a1 = [end[0] + 0.25 * (start[0] - end[0]) - 0.12 * (start[1] - end[1]),
              end[1] + 0.25 * (start[1] - end[1]) + 0.12 * (start[0] - end[0])]
        a2 = [end[0] + 0.25 * (start[0] - end[0]) + 0.12 * (start[1] - end[1]),
              end[1] + 0.25 * (start[1] - end[1]) - 0.12 * (start[0] - end[0])]

        self._add_line(start, end, min(z1, z2), color, width)
        self._add_line(a1, end, min(z1, z2), color, width)
        self._add_line(a2, end, min(z1, z2), color, width)

    def add_math(self, text, position, anchor="center", color="black"):
        position, z = self.map_to_2d(position)
        math = {"type": "math",
                "z-value": z + self._zadd,
                "text": text,
                "position": position,
                "anchor": anchor,
                "color": color}
        self._items.append(math)

    def add_to_origin(self, x=None, y=None):
        if x is not None:
            self.origin[0] += x
        if y is not None:
            self.origin[1] += y

    def set_origin(self, x=None, y=None):
        if x is not None:
            self.origin[0] = x
        if y is not None:
            self.origin[1] = y

    def add_axes(self, tdim):
        if tdim == 1:
            self.add_arrow((0, 0), (34, 0))
            self.add_math("x", (37, 0), "west")
        if tdim == 2:
            self.add_arrow((0, 0), (34, 0))
            self.add_arrow((0, 0), (0, 34))
            self.add_math("x", (37, 0), "west")
            self.add_math("y", (0, 40), "south")
        if tdim == 3:
            self.add_arrow((0, 0, 0), (34, 0, 0))
            self.add_arrow((0, 0, 0), (0, 34, 0))
            self.add_arrow((0, 0, 0), (0, 0, 34))
            self.add_math("x", (37, 0, 0), "west")
            self.add_math("y", (0, 40, 0), "south west")
            self.add_math("z", (0, 0, 40), "south")
        self.set_origin(x=self.width + self.padding * 3)

    def add_dof_number(self, position, number, color="black"):
        position, z = self.map_to_2d(position)
        dofn = {"type": "dofn",
                "z-value": z + self._zadd,
                "number": number,
                "position": position,
                "color": color}
        self._items.append(dofn)

    def add_fill(self, vertices, color="black"):
        new_v = []
        z = None
        for v in vertices:
            v, _z = self.map_to_2d(v)
            if z is None:
                z = _z
            z = min(z, _z)
            new_v.append(v)
        fill = {"type": "fill",
                "z-value": z - self._zadd,
                "vertices": new_v,
                "color": color}
        self._items.append(fill)

    def to_svg(self, offset=(0, 0)):
        out = f"<svg width='{self.width + offset[0]}' height='{self.height + offset[1]}'>"

        self._items.sort(key=lambda x: x["z-value"])

        for i in self._items:
            if i["type"] == "fill":
                out += "<polygon points='"
                out += " ".join([f"{float(offset[0] + j)},{float(offset[1] + self.height - k)}"
                                 for j, k in i["vertices"]])
                out += f"' fill='{i['color']}' />"
            elif i["type"] == "math":
                assert i["color"] == "black"
                out += f"<text x='{float(offset[0] + i['position'][0])}' "
                out += f"y='{float(offset[1] + self.height - i['position'][1])}' "
                out += "class='small' "
                if "south" in i["anchor"]:
                    out += "dominant-baseline='text-bottom' "
                elif "north" in i["anchor"]:
                    out += "dominant-baseline='text-top' "
                else:
                    out += "dominant-baseline='middle' "
                if "west" in i["anchor"]:
                    out += "text-anchor='start' "
                elif "east" in i["anchor"]:
                    out += "text-anchor='end' "
                else:
                    out += "text-anchor='middle' "
                out += f"style='font-family:MJXZERO, MJXTEX-I'>{i['text']}</text>\n"
            elif i["type"] == "line":
                out += f"<line x1='{float(offset[0] + i['start'][0])}' "
                out += f"y1='{float(offset[1] + self.height - i['start'][1])}' "
                out += f"x2='{float(offset[0] + i['end'][0])}' "
                out += f"y2='{float(offset[1] + self.height - i['end'][1])}' "
                out += f"stroke-width='{i['width']}' stroke-linecap='round' "
                out += f"stroke='{i['color']}' />\n"
            elif i["type"] == "bezier":
                out += "<path d='"
                out += f"M {float(offset[0] + i['start'][0])} "
                out += f"{float(offset[1] + self.height - i['start'][1])} "
                out += f"C {float(offset[0] + i['mid1'][0])} "
                out += f"{float(offset[1] + self.height - i['mid1'][1])}, "
                out += f" {float(offset[0] + i['mid2'][0])} "
                out += f"{float(offset[1] + self.height - i['mid2'][1])}, "
                out += f" {float(offset[0] + i['end'][0])} "
                out += f"{float(offset[1] + self.height - i['end'][1])}' "
                out += f"stroke-width='{i['width']}' stroke-linecap='round' "
                out += f"stroke='{i['color']}' fill='none' />\n"
            elif i["type"] == "dofn":
                out += f"<circle cx='{float(offset[0] + i['position'][0])}' "
                out += f"cy='{float(offset[1] + self.height - i['position'][1])}' "
                out += f"r='10px' fill='white' stroke='{i['color']}' "
                out += "stroke-width='2px' />"
                out += f"<text x='{float(offset[0] + i['position'][0])}' "
                out += f"y='{float(offset[1] + self.height - i['position'][1])}' "
                out += "text-anchor='middle' dominant-baseline='middle'"
                if i["number"] >= 10:
                    out += " style='font-size:70%'"
                out += f" fill='{i['color']}'>{i['number']}</text>"
            else:
                raise ValueError(f"Unknown item type: {i['type']}")

        out += "</svg>"
        return out

    def to_tikz(self, offset=(0, 0), reduce_padding=0, reduce_padding_x=None, reduce_padding_y=None,
                include_begin_end=True, debug_bg=False):
        if reduce_padding_x is None:
            reduce_padding_x = reduce_padding
        if reduce_padding_y is None:
            reduce_padding_y = reduce_padding

        out = ""
        if include_begin_end:
            out += "\\begin{tikzpicture}[x=0.2mm,y=0.2mm]\n"

        colors = {}
        for i in self._items:
            if i["color"] not in colors:
                if i["color"][0] == "#":
                    out += f"\\definecolor{{color{len(colors)}}}{{HTML}}{{{i['color'][1:]}}}\n"
                    colors[i["color"]] = f"color{len(colors)}"
                else:
                    colors[i["color"]] = i["color"]

        out += f"\\clip ({reduce_padding_x},{reduce_padding_y}) rectangle "
        out += f"({self.width + offset[0] - reduce_padding_x},"
        out += f"{self.height + offset[1] - reduce_padding_y});\n"

        if debug_bg:
            out += f"\\fill[red] ({reduce_padding_x},{reduce_padding_y}) rectangle "
            out += f"({self.width + offset[0] - reduce_padding_x},"
            out += f"{self.height + offset[1] - reduce_padding_y});\n"

        self._items.sort(key=lambda x: x["z-value"])

        for i in self._items:
            if i["type"] == "fill":
                out += f"\\fill[{colors[i['color']]}] "
                out += " -- ".join([f"({float(offset[0] + j)},{float(offset[1] + k)})"
                                    for j, k in i["vertices"]])
                out += " -- cycle;\n"
            elif i["type"] == "math":
                assert i["color"] == "black"
                out += f"\\node[anchor={i['anchor']}] "
                out += f"at ({float(offset[0] + i['position'][0])},"
                out += f"{float(offset[1] + i['position'][1])}) "
                out += f"{{${i['text']}$}};\n"
            elif i["type"] == "line":
                out += f"\\draw[{colors[i['color']]},"
                out += f"line width={i['width'].replace('px', 'pt')},line cap=round]"
                out += f"({float(offset[0] + i['start'][0])},{float(offset[1] + i['start'][1])})"
                out += " -- "
                out += f"({float(offset[0] + i['end'][0])},{float(offset[1] + i['end'][1])});\n"
            elif i["type"] == "bezier":
                out += f"\\draw[{colors[i['color']]},"
                out += f"line cap=round,line width={i['width'].replace('px', 'pt')}] "
                out += f"({float(offset[0] + i['start'][0])},{float(offset[1] + i['start'][1])})"
                out += " .. controls "
                out += f"({float(offset[0] + i['mid1'][0])},{float(offset[1] + i['mid1'][1])})"
                out += " and "
                out += f"({float(offset[0] + i['mid2'][0])},{float(offset[1] + i['mid2'][1])})"
                out += " .. "
                out += f"({float(offset[0] + i['end'][0])},{float(offset[1] + i['end'][1])})"
                out += ";\n"
            elif i["type"] == "dofn":
                out += f"\\draw[{colors[i['color']]},fill=white,line width=1.5pt] "
                out += f"({float(offset[0] + i['position'][0])},"
                out += f"{float(offset[1] + i['position'][1])})"
                out += "circle (6pt);\n"
                out += f"\\node[anchor=center] at ({float(offset[0] + i['position'][0])},"
                out += f"{float(offset[1] + i['position'][1])}) {{"
                if i["number"] >= 10:
                    out += "\\tiny"
                else:
                    out += "\\small"
                out += f"\\color{{{colors[i['color']]}}}{i['number']}}};\n"
            else:
                raise ValueError(f"Unknown item type: {i['type']}")

        if include_begin_end:
            out += "\\end{tikzpicture}"
        return out


def make_lattice(element, n, offset=False, pairs=False):
    ref = element.reference
    f = element.get_basis_functions()[0]
    if isinstance(f, PiecewiseFunction):
        m = n // 2
        if offset:
            assert not pairs
            points = []
            for piece in f.pieces:
                assert len(piece[0]) == 3
                og = [float(i) for i in piece[0][0]]
                a0 = [float(i - j) for i, j in zip(piece[0][1], piece[0][0])]
                a1 = [float(i - j) for i, j in zip(piece[0][2], piece[0][0])]
                points += [(og[0] + a0[0] * (i + 0.5) / (m + 1) + a1[0] * (j + 0.5) / (m + 1),
                            og[1] + a0[1] * (i + 0.5) / (m + 1) + a1[1] * (j + 0.5) / (m + 1))
                           for i in range(m) for j in range(m - i)]
            return points
        else:
            all_points = []
            pairlist = []
            s = 0
            for j in range(m-1, 0, -1):
                pairlist += [(i, i+1) for i in range(s, s+j)]
                s += j + 1
            for k in range(m + 1):
                s = k
                for i in range(m, k, -1):
                    if i != k + 1:
                        pairlist += [(s, s + i)]
                    if k != 0:
                        pairlist += [(s, s + i - 1)]
                    s += i
            for piece in f.pieces:
                assert len(piece[0]) == 3
                og = [float(i) for i in piece[0][0]]
                a0 = [float(i - j) for i, j in zip(piece[0][1], piece[0][0])]
                a1 = [float(i - j) for i, j in zip(piece[0][2], piece[0][0])]
                all_points.append(
                    [(og[0] + a0[0] * i / (m - 1) + a1[0] * j / (m - 1),
                      og[1] + a0[1] * i / (m - 1) + a1[1] * j / (m - 1))
                     for i in range(m) for j in range(m - i)]
                )
            return all_points, [pairlist for p in all_points]

    if ref.name == "interval":
        if offset:
            points = [((i + 0.5) / (n + 1), ) for i in range(n)]
        else:
            points = [(i / (n - 1), ) for i in range(n)]
    elif ref.name == "triangle":
        if offset:
            points = [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1))
                      for i in range(n) for j in range(n - i)]
        else:
            points = [(i / (n - 1), j / (n - 1)) for i in range(n) for j in range(n - i)]
    elif ref.name == "tetrahedron":
        if offset:
            points = [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1), (k + 0.5) / (n + 1))
                      for i in range(n) for j in range(n - i) for k in range(n - i - j)]
        else:
            points = [(i / (n - 1), j / (n - 1), k / (n - 1))
                      for i in range(n) for j in range(n - i) for k in range(n - i - j)]
    elif ref.name == "quadrilateral":
        if offset:
            points = [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1))
                      for i in range(n + 1) for j in range(n + 1)]
        else:
            points = [(i / (n - 1), j / (n - 1)) for i in range(n) for j in range(n)]
    elif ref.name == "hexahedron":
        if offset:
            points = [((i + 0.5) / (n + 1), (j + 0.5) / (n + 1), (k + 0.5) / (n + 1))
                      for i in range(n + 1) for j in range(n + 1) for k in range(n + 1)]
        else:
            points = [(i / (n - 1), j / (n - 1), k / (n - 1))
                      for i in range(n) for j in range(n) for k in range(n)]
    else:
        raise ValueError("Unknown cell type.")

    if not pairs:
        return points

    assert not offset
    ref = element.reference

    if ref.tdim == 1:
        pairlist = [(i, i+1) for i, j in enumerate(points[:-1])]
    elif ref.tdim == 2:
        pairlist = []
        if ref.name == "triangle":
            s = 0
            for j in range(n-1, 0, -1):
                pairlist += [(i, i+1) for i in range(s, s+j)]
                s += j + 1
            for k in range(n + 1):
                s = k
                for i in range(n, k, -1):
                    if i != k + 1:
                        pairlist += [(s, s + i)]
                    if k != 0:
                        pairlist += [(s, s + i - 1)]
                    s += i
        elif ref.name == "quadrilateral":
            for i in range(n):
                for j in range(n):
                    node = i * n + j
                    if j != n - 1:
                        pairlist += [(node, node + 1)]
                    if i != n - 1:
                        pairlist += [(node, node + n)]
                        if j != 0:
                            pairlist += [(node, node + n - 1)]
    return points, pairlist


def get_apply_scale(ref):
    if ref.name == "dual polygon":
        return lambda p: [j * 50 + 50 if i < 2 else j * 100 for i, j in enumerate(p)]
    return lambda p: [i * 100 for i in p]


def plot_reference(ref):
    apply_scale = get_apply_scale(ref)

    p = Plot()
    p.add_axes(ref.tdim)

    for d in range(ref.tdim + 1):
        for edge in ref.edges:
            v1 = apply_scale(ref.vertices[edge[0]])
            v2 = apply_scale(ref.vertices[edge[1]])
            p.add_line(v1, v2)

        for i, e in enumerate(ref.sub_entities(d)):
            if d == 0:
                p.add_dof_number(apply_scale(e), i, ENTITY_COLORS[d])
            else:
                pos = apply_scale(
                    [sum(k) / len(k) for k in zip(*[ref.vertices[j] for j in e])])
                p.add_dof_number(pos, i, ENTITY_COLORS[d])

        p.set_origin(x=p.width + p.padding)

    return p


def plot_function(element, dof_i):
    return plot_basis_functions(element)[dof_i]


def plot_basis_functions(element):
    if element.range_dim == 1:
        if element.domain_dim > 2:
            return [NoPlot() for i in range(element.space_dim)]
    else:
        if element.range_dim != element.domain_dim:
            return [NoPlot() for i in range(element.space_dim)]

    def _norm(a):
        try:
            a = float(a)
            return abs(a)
        except TypeError:
            return sum(i ** 2 for i in a) ** 0.5

    def _to_float(a):
        try:
            return float(a)
        except TypeError:
            return [_to_float(b) for b in a]

    if element.range_dim == 1:
        points, pairs = make_lattice(element, 6, offset=False, pairs=True)
    else:
        points = make_lattice(element, 6, offset=True)

    f = element.get_basis_functions()[0]
    if element.range_dim == 1 and isinstance(f, PiecewiseFunction):
        scale = 1  # max(max(_norm(j) for j in i) for i in tab)
        apply_scale = get_apply_scale(element.reference)

        ps = []
        for dofn, function in enumerate(element.get_basis_functions()):
            p = Plot(dim=element.domain_dim + 1, padding=30)

            if len(element.dofs) > 0:
                dof = element.dofs[dofn]

                if dof.entity[0] >= 2:
                    if dof.entity[0] == 2:
                        faces = [dof.entity[1]]
                    else:
                        faces = [i for i, _ in enumerate(element.reference.faces)]
                    for f in faces:
                        vertices = [apply_scale(element.reference.vertices[i])
                                    for i in element.reference.faces[f]]
                        if len(vertices) == 4:
                            vertices = [vertices[0], vertices[1], vertices[3], vertices[2]]
                        p.add_fill(vertices, color=COLORS["light blue"])

            for en, edge in enumerate(element.reference.edges):
                v1 = apply_scale(element.reference.vertices[edge[0]])
                v2 = apply_scale(element.reference.vertices[edge[1]])
                if len(element.dofs) > 0 and dof.entity[0] == 1 and dof.entity[1] == en:
                    p.add_line(v1, v2, color=COLORS["blue"])
                else:
                    p.add_line(v1, v2, color=COLORS["gray"])

            for pts, prs, (_, f) in zip(points, pairs, function.pieces):
                evals = [subs(f, x, p) for p in pts]

                deriv = grad(f, element.domain_dim)
                for i, j in prs:
                    d_pi = tuple(2 * a / 3 + b / 3 for a, b in zip(pts[i], pts[j]))
                    d_pj = tuple(a / 3 + 2 * b / 3 for a, b in zip(pts[i], pts[j]))
                    di = vdot(subs(deriv, x, pts[i]), vsub(d_pi, pts[i]))
                    dj = vdot(subs(deriv, x, pts[j]), vsub(d_pj, pts[j]))
                    p.add_bezier(apply_scale(tuple(pts[i]) + (evals[i] / scale, )),
                                 apply_scale(d_pi + ((evals[i] + di) / scale, )),
                                 apply_scale(d_pj + ((evals[j] + dj) / scale, )),
                                 apply_scale(tuple(pts[j]) + (evals[j] / scale, )),
                                 width="2px", color=COLORS["orange"])

            if len(element.dofs) > 0:
                if dof.dof_direction() is not None:
                    p.add_arrow(apply_scale(dof.dof_point()),
                                apply_scale([i + j / 4 for i, j in zip(dof.dof_point(),
                                                                       dof.dof_direction())]),
                                width="2px", color=COLORS["purple"])
                p.add_dof_number(apply_scale(dof.dof_point()), dofn, color=COLORS["purple"])

            ps.append(p)
        return ps
    else:
        tab = _to_float(element.tabulate_basis(points, "xyz,xyz"))

        scale = max(max(_norm(j) for j in i) for i in tab)
        apply_scale = get_apply_scale(element.reference)

        ps = []
        for dofn, function in enumerate(element.get_basis_functions()):
            if element.range_dim == 1:
                assert element.domain_dim <= 2
                p = Plot(dim=element.domain_dim + 1, padding=30)
            else:
                assert element.range_dim == element.domain_dim
                p = Plot(dim=element.domain_dim, padding=30)

            if len(element.dofs) > 0:
                dof = element.dofs[dofn]

                if dof.entity[0] >= 2:
                    if dof.entity[0] == 2:
                        faces = [dof.entity[1]]
                    else:
                        faces = [i for i, _ in enumerate(element.reference.faces)]
                    for f in faces:
                        vertices = [apply_scale(element.reference.vertices[i])
                                    for i in element.reference.faces[f]]
                        if len(vertices) == 4:
                            vertices = [vertices[0], vertices[1], vertices[3], vertices[2]]
                        p.add_fill(vertices, color=COLORS["light blue"])

            for en, edge in enumerate(element.reference.edges):
                v1 = apply_scale(element.reference.vertices[edge[0]])
                v2 = apply_scale(element.reference.vertices[edge[1]])
                if len(element.dofs) > 0 and dof.entity[0] == 1 and dof.entity[1] == en:
                    p.add_line(v1, v2, color=COLORS["blue"])
                else:
                    p.add_line(v1, v2, color=COLORS["gray"])

            evals = [i[dofn] for i in tab]

            if element.range_dim == 1:
                deriv = grad(function, element.domain_dim)
                for i, j in pairs:
                    d_pi = tuple(2 * a / 3 + b / 3 for a, b in zip(points[i], points[j]))
                    d_pj = tuple(a / 3 + 2 * b / 3 for a, b in zip(points[i], points[j]))
                    di = vdot(subs(deriv, x, points[i]), vsub(d_pi, points[i]))
                    dj = vdot(subs(deriv, x, points[j]), vsub(d_pj, points[j]))
                    p.add_bezier(apply_scale(tuple(points[i]) + (evals[i] / scale, )),
                                 apply_scale(d_pi + ((evals[i] + di) / scale, )),
                                 apply_scale(d_pj + ((evals[j] + dj) / scale, )),
                                 apply_scale(tuple(points[j]) + (evals[j] / scale, )),
                                 width="2px", color=COLORS["orange"])
            else:
                assert element.range_dim == element.domain_dim

                for pt, v in zip(points, evals):
                    wid = 4 * sum(i**2 for i in v) ** 0.5 / scale
                    p.add_arrow(apply_scale(pt),
                                apply_scale([i + j / (2.5 * scale) for i, j in zip(pt, v)]),
                                color=COLORS["orange"], width=f"{wid}px")

            if len(element.dofs) > 0:
                if dof.dof_direction() is not None:
                    p.add_arrow(apply_scale(dof.dof_point()),
                                apply_scale([i + j / 4 for i, j in zip(dof.dof_point(),
                                                                       dof.dof_direction())]),
                                width="2px", color=COLORS["purple"])
                p.add_dof_number(apply_scale(dof.dof_point()), dofn, color=COLORS["purple"])
            ps.append(p)
        return ps
