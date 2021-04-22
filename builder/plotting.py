ENTITY_COLORS = ["#FF8800", "#44AAFF", "#55FF00", "#DD2299"]


class Plot:
    def __init__(self, padding=15):
        self.padding = padding
        self.height = 2 * self.padding
        self.width = 2 * self.padding
        self.origin = [self.padding, self.padding]
        self._items = []

    def map_to_2d(self, point):
        if len(point) == 0:
            return (self.origin[0], self.origin[1]), 0
        if len(point) == 1:
            return (self.origin[0] + point[0], self.origin[1]), 0
        if len(point) == 2:
            return (self.origin[0] + point[0], self.origin[1] + point[1]), 0
        if len(point) == 3:
            return (self.origin[0] + point[0], self.origin[1] + point[1]), 0

    def _add_line(self, start, end, z, color, width):
        line = {"type": "line",
                "z-value": z,
                "start": start,
                "end": end,
                "width": width,
                "color": color}
        self._items.append(line)
        self.width = max(self.width, line["start"][0] + self.padding, line["end"][0] + self.padding)
        self.height = max(self.height, line["start"][1] + self.padding, line["end"][1] + self.padding)

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
                "z-value": z + 0.2,
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
        self.set_origin(x=self.width + self.padding)

    def add_dof_number(self, position, number, dim):
        position, z = self.map_to_2d(position)
        dofn = {"type": "dofn",
                "z-value": z + 0.2,
                "text": number,
                "position": position,
                "dim": dim}
        self._items.append(dofn)

    def to_svg(self):
        out = f"<svg width='{self.width}' height='{self.height}'>"

        self._items.sort(key=lambda x: x["z-value"])

        for i in self._items:
            if i["type"] == "math":
                assert i["color"] == "black"
                out += f"<text x='{i['position'][0]}' y='{self.height - i['position'][1]}' class='small' "
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
                out += f"<line x1='{i['start'][0]}' y1='{self.height - i['start'][1]}' "
                out += f"x2='{i['end'][0]}' y2='{self.height - i['end'][1]}' "
                out += f"stroke-width='{i['width']}' stroke-linecap='round' stroke='{i['color']}' />\n"
            elif i["type"] == "dofn":
                out += f"<circle cx='{i['position'][0]}' cy='{self.height - i['position'][1]}' r='10px' fill='white'"
                out += f" stroke='{ENTITY_COLORS[i['dim']]}' stroke-width='2px' />"
                out += f"<text x='{i['position'][0]}' y='{self.height - i['position'][1]}' "
                out += "text-anchor='middle' dominant-baseline='middle'"
                out += f" fill='{ENTITY_COLORS[i['dim']]}'>{i['text']}</text>"
            else:
                raise ValueError(f"Unknown item type: {i['type']}")

        out += "</svg>"
        return out


def plot_reference(ref):
    p = Plot()
    p.add_axes(ref.tdim)

    for d in range(ref.tdim + 1):
        for edge in ref.edges:
            v1 = [100 * i for i in ref.vertices[edge[0]]]
            v2 = [100 * i for i in ref.vertices[edge[1]]]
            p.add_line(v1, v2)

        for i, e in enumerate(ref.sub_entities(d)):
            if d == 0:
                p.add_dof_number([100 * j for j in e], i, d)
            else:
                pos = [sum(k) * 100 / len(k) for k in zip(*[ref.vertices[j] for j in e])]
                p.add_dof_number(pos, i, d)

        p.set_origin(x=p.width + p.padding)

    return p.to_svg()
