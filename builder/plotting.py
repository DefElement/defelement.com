ENTITY_COLORS = ["#FF8800", "#44AAFF", "#55FF00", "#DD2299"]


class Plot:
    def __init__(self, padding=15):
        self.padding = padding
        self.height = 2 * self.padding
        self.width = 2 * self.padding
        self.origin = [self.padding, self.padding]
        self._items = []
        self._zadd = 0.00001

    def map_to_2d(self, point):
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
                self.origin[0] + point[0] + point[1] / 2,
                self.origin[1] + point[2] - 2 * point[0] / 25 + point[1] / 5
            ), point[0] - 2 * point[1] + 12 * point[2] / 25

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

    def add_dof_number(self, position, number, dim):
        position, z = self.map_to_2d(position)
        dofn = {"type": "dofn",
                "z-value": z + self._zadd,
                "number": number,
                "position": position,
                "dim": dim}
        self._items.append(dofn)

    def to_svg(self, offset=(0,0)):
        out = f"<svg width='{self.width}' height='{self.height}'>"

        self._items.sort(key=lambda x: x["z-value"])

        for i in self._items:
            if i["type"] == "math":
                assert i["color"] == "black"
                out += f"<text x='{float(i['position'][0])}' "
                out += f"y='{float(self.height - i['position'][1])}' "
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
                out += f"<line x1='{float(i['start'][0])}' "
                out += f"y1='{float(self.height - i['start'][1])}' "
                out += f"x2='{float(i['end'][0])}' y2='{float(self.height - i['end'][1])}' "
                out += f"stroke-width='{i['width']}' stroke-linecap='round' "
                out += f"stroke='{i['color']}' />\n"
            elif i["type"] == "dofn":
                out += f"<circle cx='{float(i['position'][0])}' "
                out += f"cy='{float(self.height - i['position'][1])}' "
                out += f"r='10px' fill='white' stroke='{ENTITY_COLORS[i['dim']]}' "
                out += "stroke-width='2px' />"
                out += f"<text x='{float(i['position'][0])}' "
                out += f"y='{float(self.height - i['position'][1])}' "
                out += "text-anchor='middle' dominant-baseline='middle'"
                if i["number"] >= 10:
                    out += " style='font-size:70%'"
                out += f" fill='{ENTITY_COLORS[i['dim']]}'>{i['number']}</text>"
            else:
                raise ValueError(f"Unknown item type: {i['type']}")

        out += "</svg>"
        return out


def plot_reference(ref):
    if ref.name == "dual polygon":
        apply_scale = lambda p: [i * 0.5 + 50 for i in p]
    else:
        apply_scale = lambda p: p
    p = Plot()
    p.add_axes(ref.tdim)

    for d in range(ref.tdim + 1):
        for edge in ref.edges:
            v1 = apply_scale([100 * i for i in ref.vertices[edge[0]]])
            v2 = apply_scale([100 * i for i in ref.vertices[edge[1]]])
            p.add_line(v1, v2)

        for i, e in enumerate(ref.sub_entities(d)):
            if d == 0:
                p.add_dof_number(apply_scale([100 * j for j in e]), i, d)
            else:
                pos = apply_scale(
                    [sum(k) * 100 / len(k) for k in zip(*[ref.vertices[j] for j in e])])
                p.add_dof_number(pos, i, d)

        p.set_origin(x=p.width + p.padding)

    return p.to_svg()
