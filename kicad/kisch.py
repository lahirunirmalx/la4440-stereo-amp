"""Minimal KiCad 9 schematic writer.

Symbols are flattened out of the system libraries into lib_symbols, placed
on the sheet with a rotation, and their absolute pin coordinates are computed
so wires can be drawn pin to pin. Library coordinates are Y-up; the sheet is
Y-down, so an unrotated pin at lib (0, 3.81) lands at (X, Y - 3.81).
"""
import re
import uuid
from pathlib import Path

LIBDIR = Path("/usr/share/kicad/symbols")


def uid():
    return str(uuid.uuid4())


def _block(text, name):
    """Return the full (symbol "name" ...) block from a library file."""
    i = text.find('(symbol "%s"' % name)
    if i < 0:
        raise KeyError(name)
    depth = 0
    for k in range(i, len(text)):
        if text[k] == "(":
            depth += 1
        elif text[k] == ")":
            depth -= 1
            if depth == 0:
                return text[i:k + 1]
    raise ValueError(name)


def _set_prop(blk, prop, value):
    pat = r'\(property "%s" "[^"]*"' % prop
    if re.search(pat, blk):
        return re.sub(pat, '(property "%s" "%s"' % (prop, value), blk, count=1)
    return blk


def load_symbol(lib, name, new_name=None, props=None, pin_renames=None, libfile=None):
    """Flatten lib:name (following one level of extends) into a lib_symbols
    entry called lib:new_name. props overrides Value/Footprint/...; pin_renames
    maps pin number -> (new name, new electrical type)."""
    text = Path(libfile).read_text() if libfile else (LIBDIR / (lib + ".kicad_sym")).read_text()
    blk = _block(text, name)
    m = re.search(r'\(extends "([^"]+)"\)', blk)
    if m:
        parent = _block(text, m.group(1))
        # child properties, parent body
        child_props = dict(re.findall(r'\(property "([^"]+)" "([^"]*)"', blk))
        blk = parent
        for k, v in child_props.items():
            blk = _set_prop(blk, k, v)
        blk = blk.replace('(symbol "%s_' % m.group(1), '(symbol "%s_' % name)
        blk = blk.replace('(symbol "%s"' % m.group(1), '(symbol "%s"' % name, 1)
    new_name = new_name or name
    full = "%s:%s" % (lib, new_name)
    blk = blk.replace('(symbol "%s"' % name, '(symbol "%s"' % full, 1)
    blk = blk.replace('(symbol "%s_' % name, '(symbol "%s_' % new_name)
    for k, v in (props or {}).items():
        blk = _set_prop(blk, k, v)
    if pin_renames:
        parts = blk.split("(pin ")
        for i in range(1, len(parts)):
            m = re.search(r'\(number "([^"]+)"', parts[i])
            if m and m.group(1) in pin_renames:
                nm, et = pin_renames[m.group(1)]
                parts[i] = re.sub(r'^\w+ line', et + ' line', parts[i], count=1)
                parts[i] = re.sub(r'\(name "[^"]*"', '(name "%s"' % nm, parts[i], count=1)
        blk = "(pin ".join(parts)
    pins = {}
    for pm in re.finditer(r'\(pin (\w+) line\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\)\s*\(length ([\d.]+)\)(?:\s*\(hide yes\))?\s*\(name "([^"]*)"', blk):
        num = re.search(r'\(number "([^"]+)"', blk[pm.end():pm.end() + 300]).group(1)
        pins[num] = (float(pm.group(2)), float(pm.group(3)), pm.group(6), pm.group(1))
    return full, blk, pins


class Sch:
    def __init__(self, title, paper="A3"):
        self.title = title
        self.paper = paper
        self.uuid = uid()
        self.libs = {}       # full name -> (block, pins)
        self.items = []
        self.pinpos = {}     # "REF.num" -> (x, y)
        self.refs = {}       # ref -> (lib full name, uuid)
        self.pwr_n = 0
        self.wires = []
        self.junctions = []

    def lib(self, lib, name, **kw):
        full, blk, pins = load_symbol(lib, name, **kw)
        self.libs[full] = (blk, pins)
        return full

    def place(self, full, ref, value, x, y, rot=0, mirror=None, footprint="",
              ref_at=None, val_at=None, hide_value=False, on_board=True):
        blk, pins = self.libs[full]
        u = uid()
        if ref.startswith("#"):
            self.pwr_n += 1
            ref = "%s%02d" % (ref, self.pwr_n)
        self.refs[ref] = (full, u)
        import math
        a = math.radians(rot)
        c, s = round(math.cos(a)), round(math.sin(a))
        for num, (px, py, nm, et) in pins.items():
            # verified against kicad-cli netlists (t/probe): rotate in lib
            # space (Y-up), then flip to the Y-down sheet, then apply the
            # mirror in SHEET space. rot 90 puts lib pin (0, 3.81) on the left.
            rx = px * c - py * s
            ry = px * s + py * c
            sx, sy = rx, -ry
            if mirror == "y":
                sx = -sx
            elif mirror == "x":
                sy = -sy
            self.pinpos["%s.%s" % (ref, num)] = (round(x + sx, 3), round(y + sy, 3))
        prot = 0 if rot == 180 else (360 - rot) % 360
        rx_, ry_ = ref_at or (x + 2.54, y - 1.27)
        vx_, vy_ = val_at or (x + 2.54, y + 1.27)
        mir = '\n\t\t(mirror %s)' % mirror if mirror else ""
        pins_s = "".join('\n\t\t(pin "%s"\n\t\t\t(uuid "%s")\n\t\t)' % (n, uid()) for n in pins)
        hv = "\n\t\t\t\t(hide yes)" if hide_value else ""
        self.items.append('''	(symbol
		(lib_id "%s")
		(at %s %s %d)%s
		(unit 1)
		(exclude_from_sim no)
		(in_bom %s)
		(on_board %s)
		(dnp no)
		(uuid "%s")
		(property "Reference" "%s"
			(at %s %s %d)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)%s
			)
		)
		(property "Value" "%s"
			(at %s %s %d)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)%s
			)
		)
		(property "Footprint" "%s"
			(at %s %s 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" ""
			(at %s %s 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Description" ""
			(at %s %s 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)%s
		(instances
			(project "%s"
				(path "/%s"
					(reference "%s")
					(unit 1)
				)
			)
		)
	)''' % (full, x, y, rot, mir, "no" if ref.startswith("#") else "yes",
            "no" if ref.startswith("#") else "yes", u, ref, rx_, ry_, prot,
            "\n\t\t\t\t(hide yes)" if ref.startswith("#") else "",
            value, vx_, vy_, prot, hv, footprint, x, y, x, y, x, y, pins_s,
            self.title, self.uuid, ref))
        return ref

    def pin(self, name):
        return self.pinpos[name]

    def wire(self, *pts):
        """Axis-aligned polyline. Segments are stored and emitted by render(),
        split at every junction, wire end and pin that lies on them: KiCad
        only joins wires at their endpoints, so a junction in the middle of
        an unsplit wire silently disconnects it."""
        for a, b in zip(pts, pts[1:]):
            if a[0] != b[0] and a[1] != b[1]:
                raise ValueError("wire %s -> %s not axis aligned" % (a, b))
            if a == b:
                continue
            self.wires.append((a, b))

    def _emit_wires(self):
        pts = set(self.pinpos.values()) | set(self.junctions)
        for a, b in self.wires:
            pts.add(a)
            pts.add(b)
        out = []
        for a, b in self.wires:
            if a[0] == b[0]:
                inside = sorted(p for p in pts if p[0] == a[0]
                                and min(a[1], b[1]) < p[1] < max(a[1], b[1]))
                inside.sort(key=lambda p: p[1], reverse=a[1] > b[1])
            else:
                inside = sorted(p for p in pts if p[1] == a[1]
                                and min(a[0], b[0]) < p[0] < max(a[0], b[0]))
                inside.sort(key=lambda p: p[0], reverse=a[0] > b[0])
            chain = [a] + inside + [b]
            for p, q in zip(chain, chain[1:]):
                out.append('''	(wire
		(pts
			(xy %s %s) (xy %s %s)
		)
		(stroke
			(width 0)
			(type default)
		)
		(uuid "%s")
	)''' % (p[0], p[1], q[0], q[1], uid()))
        return out

    def junction(self, p):
        self.junctions.append(p)
        self.items.append('''	(junction
		(at %s %s)
		(diameter 0)
		(color 0 0 0 0)
		(uuid "%s")
	)''' % (p[0], p[1], uid()))

    def label(self, p, name, rot=0):
        just = {0: "left bottom", 180: "right bottom", 90: "left bottom", 270: "right bottom"}[rot]
        self.items.append('''	(label "%s"
		(at %s %s %d)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify %s)
		)
		(uuid "%s")
	)''' % (name, p[0], p[1], rot, just, uid()))

    def no_connect(self, p):
        self.items.append('''	(no_connect
		(at %s %s)
		(uuid "%s")
	)''' % (p[0], p[1], uid()))

    def text(self, p, s, size=1.27):
        self.items.append('''	(text "%s"
		(exclude_from_sim no)
		(at %s %s 0)
		(effects
			(font
				(size %s %s)
			)
			(justify left bottom)
		)
		(uuid "%s")
	)''' % (s, p[0], p[1], size, size, uid()))

    def render(self):
        libs = "\n".join("\t" + self.libs[k][0].replace("\n", "\n\t").rstrip() if False else self.libs[k][0]
                         for k in self.libs)
        return '''(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "9.0")
	(uuid "%s")
	(paper "%s")
	(title_block
		(title "%s")
	)
	(lib_symbols
%s
	)
%s
%s
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
	(embedded_fonts no)
)
''' % (self.uuid, self.paper, self.title, libs, "\n".join(self.items), "\n".join(self._emit_wires()))

    def write(self, path):
        Path(path).write_text(self.render())
