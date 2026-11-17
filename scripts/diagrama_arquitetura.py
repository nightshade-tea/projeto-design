#!/usr/bin/env python3
# Gera docs/diagramas/arquitetura.svg (diagrama UML de pacotes e classes)
# Uso: python3 scripts/diagrama_arquitetura.py
from pathlib import Path

try:
    from PIL import ImageFont
except ImportError:
    ImageFont = None

W = 1240
FONT = "Helvetica, Arial, 'Liberation Sans', sans-serif"
out = []


def add(s):
    out.append(s)


# Fontes usadas para medir textos. Usa a mais larga entre Arial e DejaVu Sans
# (fallback comum quando não há Helvetica/Arial), para não cortar texto.
FONT_DIRS = ["/usr/share/fonts/truetype/msttcorefonts",
             "/usr/share/fonts/truetype/liberation",
             "/usr/share/fonts/truetype/dejavu",
             "/Library/Fonts", "/System/Library/Fonts/Supplemental",
             "C:/Windows/Fonts"]
FONT_FILES = {
    (False, False): ["Arial.ttf", "arial.ttf", "LiberationSans-Regular.ttf",
                     "DejaVuSans.ttf"],
    (True, False): ["arialbd.ttf", "Arial Bold.ttf", "LiberationSans-Bold.ttf",
                    "DejaVuSans-Bold.ttf"],
    (False, True): ["Arial_Italic.ttf", "ariali.ttf", "Arial Italic.ttf",
                    "LiberationSans-Italic.ttf", "DejaVuSans-Oblique.ttf"],
    (True, True): ["Arial_Bold_Italic.ttf", "arialbi.ttf",
                   "Arial Bold Italic.ttf", "LiberationSans-BoldItalic.ttf",
                   "DejaVuSans-BoldOblique.ttf"],
}
_font_cache = {}


def measure(s, size=14, bold=False, italic=False):
    """Largura do texto em px (a maior entre as fontes encontradas)"""
    widths = []
    if ImageFont:
        for d in FONT_DIRS:
            for f in FONT_FILES[(bold, italic)]:
                path = Path(d) / f
                if not path.exists():
                    continue
                key = (str(path), size)
                if key not in _font_cache:
                    _font_cache[key] = ImageFont.truetype(str(path), size)
                widths.append(_font_cache[key].getlength(s))
    if widths:
        return max(widths)
    # estimativa conservadora (métricas da DejaVu Sans)
    return len(s) * size * (0.72 if bold else 0.64)


def measure_tab(s, size=14):
    """Largura do texto em negrito na primeira fonte com métricas de
    Helvetica/Arial (Arial ou Liberation Sans), ou DejaVu se não houver"""
    if ImageFont:
        for f in FONT_FILES[(True, False)]:
            for d in FONT_DIRS:
                path = Path(d) / f
                if path.exists():
                    key = (str(path), size)
                    if key not in _font_cache:
                        _font_cache[key] = ImageFont.truetype(str(path), size)
                    return _font_cache[key].getlength(s)
    return measure(s, size, bold=True)


def fit_size(names, w, size=14, bold=True, italic=False, pad=16, min_size=10):
    """Maior tamanho de fonte <= size em que todos os nomes cabem em w"""
    while size > min_size and any(
            measure(n, size, bold, italic) > w - pad for n in names):
        size -= 0.5
    return size


def text(x, y, s, size=14, anchor="middle", weight="normal", style="normal",
         fill="#111"):
    add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
        f'font-weight="{weight}" font-style="{style}" fill="{fill}">{s}</text>')


def rect(x, y, w, h, fill="#fff", stroke="#222", sw=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def package(x, y, w, h, name, fill="#f7f7f7", tab_w=None, size=14):
    """Pacote UML com aba (nome) e corpo. y é o topo da aba"""
    tab_h = 22
    tab_w = max(tab_w or 0, measure_tab(name, size) + 20)
    rect(x, y, tab_w, tab_h, fill=fill)
    rect(x, y + tab_h, w, h, fill=fill)
    text(x + 10, y + 16, name, size=size, anchor="start", weight="bold")
    return y + tab_h  # topo do corpo


def cls(x, y, w, h, name, stereo=None, italic=False, size=14):
    rect(x, y, w, h, fill="#fff")
    cx = x + w / 2
    st = "italic" if italic else "normal"
    if stereo and "::" in name:
        # nome qualificado quebrado depois do "::" para caber na caixa
        pacote, nome = name.split("::")
        text(cx, y + h / 2 - 13, f"«{stereo}»", size=12, fill="#444")
        text(cx, y + h / 2 + 5, pacote + "::", size=size, weight="bold",
             style=st)
        text(cx, y + h / 2 + 5 + size + 4, nome, size=size, weight="bold",
             style=st)
    elif stereo:
        text(cx, y + h / 2 - 4, f"«{stereo}»", size=12, fill="#444")
        text(cx, y + h / 2 + 14, name, size=size, weight="bold",
             style="italic" if italic else "normal")
    else:
        text(cx, y + h / 2 + 5, name, size=size, weight="bold",
             style="italic" if italic else "normal")


def cls_row(cols, names, y, h, **kw):
    """Linha de classes com o mesmo tamanho de fonte, ajustado para caber"""
    partes = [p for n in names for p in n.replace("::", ":: ").split(" ")]
    size = fit_size(partes, min(w for _, w in cols),
                    italic=kw.get("italic", False))
    for (x, w), n in zip(cols, names):
        cls(x, y, w, h, n, size=size, **kw)


def line(x1, y1, x2, y2, dash=None, head=None, sw=1.3):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{head})"' if head else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#222" '
        f'stroke-width="{sw}"{d}{m}/>')


def columns(n, x0, width, gap):
    w = (width - gap * (n - 1)) / n
    return [(x0 + i * (w + gap), w) for i in range(n)]


# geometria geral
SX, SW = 40, 1160          # servidor
LX, LW = 70, 1100          # camadas
CX0, CW = LX + 20, LW - 40  # conteúdo das camadas
MID = W / 2

H = 1330
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="{FONT}">')
add('''<defs>
<marker id="open" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12"
 markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
<path d="M1,1 L11,6 L1,11" fill="none" stroke="#222" stroke-width="1.3"/>
</marker>
<marker id="tri" viewBox="0 0 16 16" refX="15" refY="8" markerWidth="16"
 markerHeight="16" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
<path d="M1,1 L15,8 L1,15 Z" fill="#fff" stroke="#222" stroke-width="1.3"/>
</marker>
</defs>''')
add(f'<rect width="{W}" height="{H}" fill="#fff"/>')

# ator
ax, ay = MID, 18
add(f'<circle cx="{ax}" cy="{ay + 9}" r="9" fill="#fff" stroke="#222" '
    f'stroke-width="1.3"/>')
line(ax, ay + 18, ax, ay + 40)
line(ax - 16, ay + 26, ax + 16, ay + 26)
line(ax, ay + 40, ax - 12, ay + 58)
line(ax, ay + 40, ax + 12, ay + 58)
text(ax, ay + 78, "Aluno / Professor / Administrador", size=13)

# cliente (nó UML)
def node(x, y, w, h, title, sub=None, fill="#fff"):
    dpt = 10
    add(f'<path d="M{x},{y} l{dpt},{-dpt} h{w} v{h} l{-dpt},{dpt}" '
        f'fill="#eee" stroke="#222" stroke-width="1.2"/>')
    add(f'<path d="M{x + w},{y} l{dpt},{-dpt}" stroke="#222" '
        f'stroke-width="1.2"/>')
    rect(x, y, w, h, fill=fill)


cy = 140
node(MID - 110, cy, 220, 44, "")
text(MID, cy + 27, "Cliente (navegador)", size=14, weight="bold")
line(MID, ay + 86, MID, cy - 12, head="open")

# servidor
sy = 240
line(MID, cy + 44, MID, sy - 12, head="open")
text(MID + 8, sy - 26, "HTTPS (REST/JSON)", size=12, anchor="start",
     fill="#444")
node(SX, sy, SW, 1010 - 0, "", fill="#fff")
text(SX + 16, sy + 24, "Servidor", size=15, anchor="start", weight="bold")
text(SX + 16 + measure("Servidor", 15, bold=True) + 10, sy + 24,
     "(monólito modular)", size=13, anchor="start",
     fill="#444")

# Controllers
y = sy + 44
b = package(LX, y, LW, 80, "Controllers")
cls_row(columns(4, CX0, CW, 24),
        ["ProjetoController", "FrequenciaController",
         "CertificadoController", "AutenticacaoController"], b + 20, 40)
prev_bottom = b + 80

# Services
y = prev_bottom + 50
line(MID, prev_bottom, MID, y + 22, dash="6,4", head="open")
b = package(LX, y, LW, 80, "Services")
cls_row(columns(5, CX0, CW, 20),
        ["ProjetoService", "EncerramentoService", "FrequenciaService",
         "CertificadoService", "AutenticacaoService"], b + 20, 40)
prev_bottom = b + 80

# Domínio
y = prev_bottom + 50
line(MID, prev_bottom, MID, y + 22, dash="6,4", head="open")
# membros de cada módulo: classe, classe abstrata (itálico) ou interface
# («interface» e o nome em itálico)
mods = [("certificacao", [("Certificado", "classe"),
                          ("CertificadoRepository", "interface"),
                          ("GeradorDocumentoCertificado", "interface")]),
        ("projetos", [("Projeto", "classe"), ("Atividade", "classe"),
                      ("Participacao", "classe"),
                      ("CriterioCertificacao", "interface"),
                      ("ProjetoRepository", "interface")]),
        ("identidade", [("Usuario", "abstrata"),
                        ("ProvedorIdentidade", "interface")])]
LH = 20                                         # altura de cada membro
mod_h = max(len(items) for _, items in mods) * LH + 30
dom_h = 14 + 22 + mod_h + 16
b = package(LX, y, LW, dom_h, "Domínio")
cols = columns(3, CX0, CW, 70)
KW = "«interface» "


def largura_membro(nome, tipo, size):
    if tipo == "interface":
        return measure(KW, 12) + measure(nome, size, italic=True)
    return measure(nome, size, italic=tipo == "abstrata")


size = 14
while size > 10 and any(largura_membro(n, t, size) > cols[0][1] - 20
                        for _, items in mods for n, t in items):
    size -= 0.5
for (x, w), (name, items) in zip(cols, mods):
    body = package(x, b + 14, w, mod_h, name, fill="#fff", size=13)
    yy = body + mod_h / 2 - (len(items) - 1) * LH / 2 + 5
    for i, (it, tipo) in enumerate(items):
        if tipo == "interface":
            add(f'<text x="{x + w / 2}" y="{yy + i * LH}" font-size="{size}" '
                f'text-anchor="middle" fill="#111">'
                f'<tspan font-size="12" fill="#444">{KW}</tspan>'
                f'<tspan font-style="italic">{it}</tspan></text>')
        else:
            text(x + w / 2, yy + i * LH, it, size=size,
                 style="italic" if tipo == "abstrata" else "normal")
mid_y = b + 14 + 22 + mod_h / 2
for i in range(2):
    (x1, w1), (x2, _) = cols[i], cols[i + 1]
    line(x1 + w1, mid_y, x2, mid_y, dash="6,4", head="open")
prev_bottom = b + dom_h

# Interfaces e implementações
icols = columns(4, CX0, CW, 24)
y = prev_bottom + 50
line(MID, prev_bottom, MID, y + 22, dash="6,4", head="open")
b = package(LX, y, LW, 110, "Interfaces")
# nomes qualificados (pacote::Interface): cada interface pertence a um
# módulo do domínio
ifaces = ["projetos::ProjetoRepository", "certificacao::CertificadoRepository",
          "identidade::ProvedorIdentidade",
          "certificacao::GeradorDocumentoCertificado"]
cls_row(icols, ifaces, b + 18, 74, stereo="interface", italic=True)
iface_bottom = b + 18 + 74
prev_bottom = b + 110

y = prev_bottom + 60
b = package(LX, y, LW, 80, "Infraestrutura")
impls = ["ProjetoRepositorySql", "CertificadoRepositorySql",
         "ProvedorIdentidadeInstitucional", "GeradorPdf"]
cls_row(icols, impls, b + 20, 40)
for (x, w), n in zip(icols, impls):
    line(x + w / 2, b + 20, x + w / 2, iface_bottom, dash="6,4", head="tri")
impl_bottom = b + 60
server_bottom = b + 80 + 30

# ajusta altura do servidor
out = [s.replace('v1010 ', f'v{server_bottom - sy} ') for s in out]
for i, s in enumerate(out):
    if s.startswith(f'<rect x="{SX}" y="{sy}" width="{SW}"'):
        out[i] = s.replace('height="1010"', f'height="{server_bottom - sy}"')
    if s.startswith(f'<path d="M{SX},{sy} l10,-10 h{SW} v1010'):
        out[i] = s.replace('v1010', f'v{server_bottom - sy}')

# sistemas externos
ey = server_bottom + 50
(x0, w0), (x1, w1), (x2, w2), _ = icols
bx = (x0 + w0 / 2 + x1 + w1 / 2) / 2
# banco de dados (cilindro)
cw, ch, rx, ry = 180, 64, 90, 10
add(f'<path d="M{bx - rx},{ey} v{ch - 2 * ry} a{rx},{ry} 0 0 0 {2 * rx},0 '
    f'v{-(ch - 2 * ry)}" fill="#fff" stroke="#222" stroke-width="1.2"/>')
add(f'<ellipse cx="{bx}" cy="{ey}" rx="{rx}" ry="{ry}" fill="#fff" '
    f'stroke="#222" stroke-width="1.2"/>')
text(bx, ey + 30, "Banco de dados", size=14, weight="bold")
for x, w in [(x0, w0), (x1, w1)]:
    add(f'<path d="M{x + w / 2},{impl_bottom} V{ey - 30} H{bx} V{ey - ry - 1}" '
        f'fill="none" stroke="#222" stroke-width="1.3" '
        f'marker-end="url(#open)"/>')
# provedor de identidade (nó externo)
px = x2 + w2 / 2
ext_name = "Provedor de identidade institucional"
ext_w = max(280, measure(ext_name, 14, bold=True) + 32)
node(px - ext_w / 2, ey, ext_w, 50, "")
text(px, ey + 21, "«externo»", size=12, fill="#444")
text(px, ey + 39, ext_name, size=14,
     weight="bold")
line(px, impl_bottom, px, ey - 12, head="open")

add('</svg>')
H2 = int(ey + 80)
out[0] = out[0].replace(f'height="{H}" viewBox="0 0 {W} {H}"', f'height="{H2}" viewBox="0 0 {W} {H2}"')
out = [o.replace(f'<rect width="{W}" height="{H}"', f'<rect width="{W}" height="{H2}"') for o in out]
dest = Path(__file__).resolve().parent.parent / "docs" / "diagramas" / "arquitetura.svg"
dest.write_text("\n".join(out) + "\n", encoding="utf-8")
print(dest)
