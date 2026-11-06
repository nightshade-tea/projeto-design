# Primitivas SVG para os diagramas UML (mesmo estilo de arquitetura.svg)
# Usado por scripts/diagrama_*.py
from html import escape
from pathlib import Path

FONTE = "Helvetica, Arial, 'Liberation Sans', sans-serif"
TINTA = "#222"
TEXTO = "#111"
SECUNDARIO = "#444"
FUNDO_PACOTE = "#f7f7f7"
TRACO = "6,4"

DESTINO = Path(__file__).resolve().parent.parent / "docs" / "diagramas"

# medidas de texto: Liberation Sans tem as mesmas métricas de Helvetica/Arial
_FONTES = {}
_ARQS = {
    (False, False): "LiberationSans-Regular.ttf",
    (True, False): "LiberationSans-Bold.ttf",
    (False, True): "LiberationSans-Italic.ttf",
    (True, True): "LiberationSans-BoldItalic.ttf",
}


def largura(s, tam=13, negrito=False, italico=False):
    chave = (tam, negrito, italico)
    if chave not in _FONTES:
        try:
            from PIL import ImageFont
            _FONTES[chave] = ImageFont.truetype(
                "/usr/share/fonts/truetype/liberation/"
                + _ARQS[(negrito, italico)], tam)
        except (ImportError, OSError):
            _FONTES[chave] = None
    f = _FONTES[chave]
    if f is None:
        return len(s) * tam * (0.62 if negrito else 0.56)
    return f.getlength(s)


class Svg:
    def __init__(self):
        self.partes = []

    def add(self, s):
        self.partes.append(s)

    def texto(self, x, y, s, tam=13, ancora="start", negrito=False,
              italico=False, cor=TEXTO):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{tam}" '
                 f'text-anchor="{ancora}" '
                 f'font-weight="{"bold" if negrito else "normal"}" '
                 f'font-style="{"italic" if italico else "normal"}" '
                 f'fill="{cor}">{escape(s)}</text>')

    def retangulo(self, x, y, w, h, fundo="#fff", espessura=1.2):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
                 f'height="{h:.1f}" fill="{fundo}" stroke="{TINTA}" '
                 f'stroke-width="{espessura}"/>')

    def linha(self, pontos, tracejado=False, inicio=None, fim=None):
        """polilinha; inicio/fim: seta, triangulo, losango, losango_vazio"""
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pontos)
        extra = f' stroke-dasharray="{TRACO}"' if tracejado else ""
        if inicio:
            extra += f' marker-start="url(#{inicio})"'
        if fim:
            extra += f' marker-end="url(#{fim})"'
        self.add(f'<polyline points="{d}" fill="none" stroke="{TINTA}" '
                 f'stroke-width="1.3"{extra}/>')

    def salvar(self, nome, w, h):
        cab = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" '
            f'height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'font-family="{FONTE}">',
            _MARCADORES,
            f'<rect width="{w:.0f}" height="{h:.0f}" fill="#fff"/>',
        ]
        destino = DESTINO / nome
        destino.write_text("\n".join(cab + self.partes + ["</svg>"]) + "\n",
                           encoding="utf-8")
        print(destino)


# marcadores; no início da linha o desenho é invertido (auto-start-reverse),
# então a ponta do losango (x=20) encosta na classe
_MARCADORES = f'''<defs>
<marker id="seta" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12"
 markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
<path d="M1,1 L11,6 L1,11" fill="none" stroke="{TINTA}" stroke-width="1.3"/>
</marker>
<marker id="triangulo" viewBox="0 0 16 16" refX="15" refY="8" markerWidth="16"
 markerHeight="16" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
<path d="M1,1 L15,8 L1,15 Z" fill="#fff" stroke="{TINTA}" stroke-width="1.3"/>
</marker>
<marker id="losango" viewBox="0 0 22 12" refX="21" refY="6" markerWidth="22"
 markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
<path d="M1,6 L11,1 L21,6 L11,11 Z" fill="{TINTA}" stroke="{TINTA}"
 stroke-width="1.2"/>
</marker>
<marker id="losango_vazio" viewBox="0 0 22 12" refX="21" refY="6"
 markerWidth="22" markerHeight="12" orient="auto-start-reverse"
 markerUnits="userSpaceOnUse">
<path d="M1,6 L11,1 L21,6 L11,11 Z" fill="#fff" stroke="{TINTA}"
 stroke-width="1.2"/>
</marker>
</defs>'''


# ---------------------------------------------------------------- classes

PAD_X = 10
LH_MEMBRO = 19
LH_NOME = 20
LH_ESTEREO = 16
TAM_MEMBRO = 13
TAM_NOME = 14
TAM_ESTEREO = 12


class Classe:
    """Classificador UML com compartimentos.

    tipo: "classe", "abstrata", "interface" ou "enumeracao".
    Classes sempre mostram os dois compartimentos (vazio = sem membros);
    classes abstratas têm o nome em itálico e a propriedade {abstract};
    interfaces mostram só operações e enumerações só os literais.
    """

    def __init__(self, nome, atributos=(), operacoes=(), tipo="classe",
                 literais=()):
        self.nome = nome
        self.tipo = tipo
        self.estereotipo = {"interface": "interface",
                            "enumeracao": "enumeration"}.get(tipo)
        if tipo in ("classe", "abstrata"):
            self.compartimentos = [list(atributos), list(operacoes)]
        elif tipo == "interface":
            self.compartimentos = [list(operacoes)]
        else:
            self.compartimentos = [list(literais)]
        self.x = self.y = 0
        self._medir()

    @property
    def italico(self):
        return self.tipo in ("interface", "abstrata")

    def _medir(self):
        ws = [largura(self.nome, TAM_NOME, True, self.italico)]
        if self.estereotipo:
            ws.append(largura(f"«{self.estereotipo}»", TAM_ESTEREO))
        if self.tipo == "abstrata":
            ws.append(largura("{abstract}", TAM_ESTEREO))
        for comp in self.compartimentos:
            ws += [largura(m, TAM_MEMBRO) for m in comp]
        self.w = max(140, max(ws) + 2 * PAD_X)
        self.h_cab = (10 + LH_NOME + (LH_ESTEREO if self.estereotipo else 0)
                      + (LH_ESTEREO if self.tipo == "abstrata" else 0))
        self.h_comps = [max(14, 8 + len(c) * LH_MEMBRO)
                        for c in self.compartimentos]
        self.h = self.h_cab + sum(self.h_comps)

    # geometria
    @property
    def esq(self):
        return self.x

    @property
    def dir(self):
        return self.x + self.w

    @property
    def topo(self):
        return self.y

    @property
    def base(self):
        return self.y + self.h

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    def mover(self, dx, dy):
        self.x += dx
        self.y += dy

    def desenhar(self, svg):
        svg.retangulo(self.x, self.y, self.w, self.h)
        y = self.y + 6
        if self.estereotipo:
            y += LH_ESTEREO
            svg.texto(self.cx, y - 3, f"«{self.estereotipo}»", TAM_ESTEREO,
                      "middle", cor=SECUNDARIO)
        y += LH_NOME
        svg.texto(self.cx, y - 4, self.nome, TAM_NOME, "middle",
                  negrito=True, italico=self.italico)
        if self.tipo == "abstrata":
            y += LH_ESTEREO
            svg.texto(self.cx, y - 5, "{abstract}", TAM_ESTEREO, "middle",
                      cor=SECUNDARIO)
        y = self.y + self.h_cab
        for comp, h in zip(self.compartimentos, self.h_comps):
            svg.add(f'<line x1="{self.x:.1f}" y1="{y:.1f}" '
                    f'x2="{self.dir:.1f}" y2="{y:.1f}" stroke="{TINTA}" '
                    f'stroke-width="1.2"/>')
            for i, m in enumerate(comp):
                svg.texto(self.x + PAD_X, y + 4 + (i + 1) * LH_MEMBRO - 5, m,
                          TAM_MEMBRO)
            y += h


# ---------------------------------------------------------------- pacotes

ABA_H = 22


def pacote(svg, x, y, w, h, nome):
    """Pacote UML: aba com o nome e corpo; y é o topo da aba, h a altura do
    corpo. Devolve o topo do corpo."""
    aba_w = largura(nome, 14, True) + 24
    svg.retangulo(x, y, aba_w, ABA_H, fundo=FUNDO_PACOTE)
    svg.retangulo(x, y + ABA_H, w, h, fundo=FUNDO_PACOTE)
    svg.texto(x + 10, y + 16, nome, 14, negrito=True)
    return y + ABA_H


def sem_sobreposicao(caixas, folga=20):
    """Falha se duas caixas (x, y, w, h, nome) ficarem a menos de `folga`."""
    for i, a in enumerate(caixas):
        for b in caixas[i + 1:]:
            if (a[0] < b[0] + b[2] + folga and b[0] < a[0] + a[2] + folga and
                    a[1] < b[1] + b[3] + folga and b[1] < a[1] + a[3] + folga):
                raise SystemExit(f"sobreposição: {a[4]} e {b[4]}")
