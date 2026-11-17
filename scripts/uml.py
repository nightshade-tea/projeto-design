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
              italico=False, cor=TEXTO, halo=False):
        """halo: contorno branco sob o texto, para cruzar linhas"""
        h = (' stroke="#fff" stroke-width="5" stroke-linejoin="round" '
             'paint-order="stroke"') if halo else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{tam}" '
                 f'text-anchor="{ancora}"{h} '
                 f'font-weight="{"bold" if negrito else "normal"}" '
                 f'font-style="{"italic" if italico else "normal"}" '
                 f'fill="{cor}">{escape(s)}</text>')

    def retangulo(self, x, y, w, h, fundo="#fff", espessura=1.2):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
                 f'height="{h:.1f}" fill="{fundo}" stroke="{TINTA}" '
                 f'stroke-width="{espessura}"/>')

    def linha(self, pontos, tracejado=False, inicio=None, fim=None):
        """polilinha com inicio e fim entre seta, seta_cheia, triangulo,
        losango e losango_vazio"""
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
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text("\n".join(cab + self.partes + ["</svg>"]) + "\n",
                           encoding="utf-8")
        print(destino)


# marcadores. No início da linha o desenho é invertido (auto-start-reverse),
# então a ponta do losango (x=20) encosta na classe
_MARCADORES = f'''<defs>
<marker id="seta" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12"
 markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
<path d="M1,1 L11,6 L1,11" fill="none" stroke="{TINTA}" stroke-width="1.3"/>
</marker>
<marker id="seta_cheia" viewBox="0 0 12 12" refX="11" refY="6"
 markerWidth="12" markerHeight="12" orient="auto-start-reverse"
 markerUnits="userSpaceOnUse">
<path d="M1,1 L11,6 L1,11 Z" fill="{TINTA}" stroke="{TINTA}" stroke-width="1"/>
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


class Caixa:
    """geometria comum a classes e componentes (x, y, w, h)"""
    x = y = w = h = 0

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


class Classe(Caixa):
    """Classificador UML com compartimentos.

    tipo: "classe", "abstrata", "interface" ou "enumeracao".
    Classes sempre mostram os dois compartimentos (vazio = sem membros).
    Classes abstratas têm o nome em itálico e a propriedade {abstract}.
    Interfaces mostram só operações, e enumerações só os literais.
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
ABA_VAZIA_W = 40


def pacote(svg, x, y, w, h, nome, nome_no_corpo=False, fundo=FUNDO_PACOTE):
    """Pacote UML com aba e corpo. y é o topo da aba, h a altura do corpo.
    Com nome_no_corpo (pacote sem conteúdo mostrado) o nome fica centrado
    no corpo e a aba fica vazia. Devolve o topo do corpo."""
    aba_w = ABA_VAZIA_W if nome_no_corpo else largura(nome, 14, True) + 24
    svg.retangulo(x, y, aba_w, ABA_H, fundo=fundo)
    svg.retangulo(x, y + ABA_H, w, h, fundo=fundo)
    if nome_no_corpo:
        svg.texto(x + w / 2, y + ABA_H + h / 2 + 5, nome, 14, "middle",
                  negrito=True)
    else:
        svg.texto(x + 10, y + 16, nome, 14, negrito=True)
    return y + ABA_H


class Pacote(Caixa):
    """Pacote UML com os membros listados no corpo e o nome na aba
    (UML 2.5: com membros mostrados no corpo, o nome vai para a aba).
    y é o topo da aba, e h inclui a aba."""

    def __init__(self, nome, membros=()):
        self.nome = nome
        self.membros = list(membros)
        self.aba_w = largura(nome, 14, True) + 24
        self.w = max(self.aba_w + 40,
                     max((largura(m, TAM_MEMBRO) for m in self.membros),
                         default=0) + 2 * 16)
        self.h = ABA_H + len(self.membros) * LH_MEMBRO + 14

    @property
    def topo_corpo(self):
        return self.y + ABA_H

    def desenhar(self, svg):
        svg.retangulo(self.x, self.y, self.aba_w, ABA_H, fundo=FUNDO_PACOTE)
        svg.retangulo(self.x, self.y + ABA_H, self.w, self.h - ABA_H,
                      fundo=FUNDO_PACOTE)
        svg.texto(self.x + 12, self.y + 16, self.nome, 14, negrito=True)
        for i, m in enumerate(self.membros):
            svg.texto(self.x + 16, self.y + ABA_H + 8 + (i + 1) * LH_MEMBRO
                      - 5, m, TAM_MEMBRO)


def sem_sobreposicao(caixas, folga=20):
    """Falha se duas caixas (x, y, w, h, nome) ficarem a menos de `folga`."""
    for i, a in enumerate(caixas):
        for b in caixas[i + 1:]:
            if (a[0] < b[0] + b[2] + folga and b[0] < a[0] + a[2] + folga and
                    a[1] < b[1] + b[3] + folga and b[1] < a[1] + a[3] + folga):
                raise SystemExit(f"sobreposição: {a[4]} e {b[4]}")


# ------------------------------------------------------------- componentes

H_CAB_COMP = 10 + LH_ESTEREO + LH_NOME
ICONE_ESPACO = 32   # reservado à direita (e, para centrar, à esquerda)


def icone_componente(svg, dir_, topo):
    """ícone UML de componente no canto superior direito"""
    x, y = dir_ - 20, topo + 8
    svg.retangulo(x, y, 12, 16, espessura=1)
    svg.retangulo(x - 4, y + 3, 8, 3.5, espessura=1)
    svg.retangulo(x - 4, y + 9.5, 8, 3.5, espessura=1)


class Componente(Caixa):
    """Componente UML: palavra-chave «component», ícone e, opcionalmente,
    o compartimento «realizations» com os classificadores que o realizam."""

    def __init__(self, nome, realizacoes=()):
        self.nome = nome
        self.realizacoes = list(realizacoes)
        ws = [largura(nome, TAM_NOME, True) + 2 * ICONE_ESPACO,
              largura("«component»", TAM_ESTEREO) + 2 * ICONE_ESPACO]
        if self.realizacoes:
            ws.append(largura("«realizations»", TAM_ESTEREO) + 2 * PAD_X)
            ws += [largura(r, TAM_MEMBRO) + 2 * PAD_X
                   for r in self.realizacoes]
        self.w = max(140, max(ws))
        self.h = H_CAB_COMP + (8 + (len(self.realizacoes) + 1) * LH_MEMBRO
                               if self.realizacoes else 0)

    def desenhar(self, svg):
        svg.retangulo(self.x, self.y, self.w, self.h)
        svg.texto(self.cx, self.y + 19, "«component»", TAM_ESTEREO, "middle",
                  cor=SECUNDARIO)
        svg.texto(self.cx, self.y + 38, self.nome, TAM_NOME, "middle",
                  negrito=True)
        icone_componente(svg, self.dir, self.y)
        if self.realizacoes:
            y = self.y + H_CAB_COMP
            svg.add(f'<line x1="{self.x:.1f}" y1="{y:.1f}" '
                    f'x2="{self.dir:.1f}" y2="{y:.1f}" stroke="{TINTA}" '
                    f'stroke-width="1.2"/>')
            svg.texto(self.cx, y + LH_MEMBRO, "«realizations»", TAM_ESTEREO,
                      "middle", cor=SECUNDARIO)
            for i, r in enumerate(self.realizacoes):
                svg.texto(self.x + PAD_X, y + (i + 2) * LH_MEMBRO, r,
                          TAM_MEMBRO)


def componente_conteiner(svg, x, y, w, h, nome, fundo=FUNDO_PACOTE):
    """componente que mostra as partes internas, com o cabeçalho à esquerda"""
    svg.retangulo(x, y, w, h, fundo=fundo)
    svg.texto(x + 12, y + 19, "«component»", TAM_ESTEREO, cor=SECUNDARIO)
    svg.texto(x + 12, y + 38, nome, TAM_NOME, negrito=True)
    icone_componente(svg, x + w, y)


R_BOLA, R_SOQUETE, PORTA = 7, 11, 12


def porta(svg, x, y):
    """porta: quadrado centrado no ponto (na borda do componente)"""
    svg.retangulo(x - PORTA / 2, y - PORTA / 2, PORTA, PORTA, espessura=1.2)


def montagem(svg, req, prov, rotulo):
    """conector de montagem: reta horizontal ou vertical do componente que
    requer a interface (soquete) ao que a fornece (bola), nome da interface
    junto da bola"""
    (x1, y1), (x2, y2) = req, prov
    comp = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    dx, dy = (x2 - x1) / comp, (y2 - y1) / comp
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    svg.linha([(x1, y1), (cx - dx * R_SOQUETE, cy - dy * R_SOQUETE)])
    nx, ny = dy, -dx
    svg.add(f'<path d="M{cx + nx * R_SOQUETE:.1f},{cy + ny * R_SOQUETE:.1f} '
            f'A{R_SOQUETE},{R_SOQUETE} 0 0 0 '
            f'{cx - nx * R_SOQUETE:.1f},{cy - ny * R_SOQUETE:.1f}" '
            f'fill="none" stroke="{TINTA}" stroke-width="1.3"/>')
    svg.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_BOLA}" fill="#fff" '
            f'stroke="{TINTA}" stroke-width="1.3"/>')
    svg.linha([(cx + dx * R_BOLA, cy + dy * R_BOLA), (x2, y2)])
    if abs(dy) < 1e-9:
        svg.texto(cx, cy - R_SOQUETE - 7, rotulo, 12, "middle")
    else:
        svg.texto(cx + R_SOQUETE + 7, cy + 4, rotulo, 12)


# ------------------------------------------------------------- interações

H_PENTAGONO = 20


def moldura(svg, x, y, w, h, operador, rotulo="", fundo="none"):
    """quadro UML (sd, loop, alt, opt...) com o rótulo no pentágono do canto
    superior esquerdo. Devolve a largura do pentágono"""
    svg.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" fill="{fundo}" stroke="{TINTA}" '
            f'stroke-width="1.2"/>')
    pw = (largura(operador, 13, True)
          + (largura(" " + rotulo, 13) if rotulo else 0) + 22)
    hp = H_PENTAGONO
    svg.add(f'<path d="M{x:.1f},{y:.1f} H{x + pw:.1f} V{y + hp - 6:.1f} '
            f'L{x + pw - 6:.1f},{y + hp:.1f} H{x:.1f} Z" fill="#fff" '
            f'stroke="{TINTA}" stroke-width="1.2"/>')
    svg.texto(x + 7, y + 15, operador, 13, negrito=True)
    if rotulo:
        svg.texto(x + 7 + largura(operador + " ", 13, True), y + 15, rotulo,
                  13)
    return pw


H_CABECA = 36
BARRA = 10          # largura da barra de ativação
ESP_MSG = 36        # distância vertical entre mensagens
GAP_LINHA = 40      # folga mínima entre cabeças vizinhas


class Sequencia:
    """Diagrama de sequência UML 2.

    - linhas de vida com a cabeça "nome : Tipo" (sem sublinhado) e a linha
      tracejada, com barras de ativação empilhadas nas chamadas aninhadas
    - chamada síncrona: linha cheia com seta cheia e o rótulo
      "operacao(argumentos)"
    - retorno: linha tracejada com seta aberta. O rótulo segue a gramática
      reply-message-label (UML 2.5.1, 17.4.4.1) e é montado a partir da
      chamada respondida, como "alvo = operacao()" ou "operacao(): valor".
      Sem alvo nem valor, o rótulo é omitido
    - criação: linha tracejada com seta aberta até a cabeça do objeto criado
    - fragmentos combinados (loop, alt, opt, break). A guarda de cada operando,
      uma condição entre colchetes, fica sobre a linha de vida do primeiro
      evento do operando
    - quadro "sd" em volta da interação
    """

    def __init__(self, nome, participantes):
        self.nome = nome
        self.chaves = [k for k, _ in participantes]
        self.rotulos = dict(participantes)
        self.eventos = []
        # chamadas ainda sem retorno, por linha de vida (para os rótulos
        # dos retornos). Os fragmentos guardam uma cópia, como no layout
        self._pendentes = {k: [] for k in self.chaves}
        self._copias = []

    # --- registro dos eventos, na ordem da interação

    def chamada(self, de, para, rotulo):
        self._pendentes[para].append(rotulo.split("(")[0])
        self.eventos.append(("chamada", de, para, rotulo))

    def retorno(self, de, para, alvo="", valor=""):
        """retorno da última chamada recebida por `de`. alvo é a variável
        que recebe o valor devolvido, e valor é o valor devolvido"""
        op = self._pendentes[de].pop()
        rotulo = ""
        if alvo or valor:
            rotulo = (f"{alvo} = " if alvo else "") + f"{op}()" + (
                f": {valor}" if valor else "")
        self.eventos.append(("retorno", de, para, rotulo))

    def criacao(self, de, para, rotulo):
        self.eventos.append(("criacao", de, para, rotulo))

    def inicio(self, operador, guarda):
        self._copias.append((operador, {k: list(v) for k, v in
                                        self._pendentes.items()}))
        self.eventos.append(("inicio", operador, guarda))

    def separador(self, guarda):
        self._pendentes = {k: list(v) for k, v in self._copias[-1][1].items()}
        self.eventos.append(("separador", guarda))

    def fim(self):
        operador, copia = self._copias.pop()
        if operador == "break":
            self._pendentes = copia
        self.eventos.append(("fim",))

    # --- layout e desenho

    def _horizontal(self, x0):
        n = len(self.chaves)
        idx = {k: i for i, k in enumerate(self.chaves)}
        self.cab_w = {k: max(110, largura(self.rotulos[k], TAM_NOME) + 24)
                      for k in self.chaves}
        gaps = [self.cab_w[a] / 2 + self.cab_w[b] / 2 + GAP_LINHA
                for a, b in zip(self.chaves, self.chaves[1:])]
        for e in self.eventos:
            if e[0] not in ("chamada", "retorno", "criacao"):
                continue
            i, j = sorted((idx[e[1]], idx[e[2]]))
            minimo = largura(e[3], 12) + 50
            if e[0] == "criacao":
                minimo += self.cab_w[e[2]] / 2
            falta = minimo - sum(gaps[i:j])
            if falta > 0:
                for g in range(i, j):
                    gaps[g] += falta / (j - i)
        self.cx = {}
        x = x0 + self.cab_w[self.chaves[0]] / 2
        for k, g in zip(self.chaves, gaps + [0]):
            self.cx[k] = x
            x += g
        self.idx = idx

    def desenhar(self, arquivo, margem=30):
        svg = Svg()
        sd_x = sd_y = margem
        self._horizontal(sd_x + 24)
        topo_cab = sd_y + H_PENTAGONO + 20
        pilhas = {k: [] for k in self.chaves}       # início das ativações
        barras = []                                  # (k, nível, y0, y1)
        cabecas = {k: topo_cab for k in self.chaves}
        mensagens = []          # (tipo, x1, x2, y, rotulo)
        quadros = []            # [operador, guarda, ytopo, [(ysep, g)], ybase, chaves]
        abertos = []
        y = topo_cab + H_CABECA + 34

        def borda(k, nivel, para_direita):
            x = self.cx[k] - BARRA / 2 + nivel * BARRA / 2
            return x + BARRA if para_direita else x

        def envolver(*ks):
            for q in abertos:
                q[5].update(ks)
            # a guarda de um operando fica sobre a linha de vida do
            # primeiro evento dele (quem envia a primeira mensagem)
            for q in abertos:
                if q[7][-1][2] is None:
                    q[7][-1][2] = ks[0]

        for e in self.eventos:
            tipo = e[0]
            if tipo == "chamada":
                _, de, para, rot = e
                if not pilhas[de]:
                    pilhas[de].append(y - 12)
                dir_ = self.cx[para] > self.cx[de]
                x1 = borda(de, len(pilhas[de]) - 1, dir_)
                pilhas[para].append(y)
                x2 = borda(para, len(pilhas[para]) - 1, not dir_)
                mensagens.append(("chamada", x1, x2, y, rot))
                envolver(de, para)
                y += ESP_MSG
            elif tipo == "retorno":
                _, de, para, rot = e
                dir_ = self.cx[para] > self.cx[de]
                nivel = len(pilhas[de]) - 1
                x1 = borda(de, nivel, dir_)
                barras.append((de, nivel, pilhas[de].pop(), y))
                x2 = borda(para, len(pilhas[para]) - 1, not dir_)
                mensagens.append(("retorno", x1, x2, y, rot))
                envolver(de, para)
                y += ESP_MSG
            elif tipo == "criacao":
                _, de, para, rot = e
                y += H_CABECA / 2 - 10
                dir_ = self.cx[para] > self.cx[de]
                x1 = borda(de, len(pilhas[de]) - 1, dir_)
                cw = self.cab_w[para]
                x2 = self.cx[para] - cw / 2 if dir_ else self.cx[para] + cw / 2
                cabecas[para] = y - H_CABECA / 2
                mensagens.append(("criacao", x1, x2, y, rot))
                envolver(de, para)
                y += H_CABECA / 2 + ESP_MSG - 8
            elif tipo == "inicio":
                # cópia das ativações: cada operando de um alt parte delas
                # operandos: [y da guarda, guarda, linha de vida]
                q = [e[1], e[2], y - 16, [], None, set(),
                     {k: list(v) for k, v in pilhas.items()},
                     [[y - 16 + H_PENTAGONO + 14, e[2], None]]]
                quadros.append(q)
                abertos.append(q)
                y += 46
            elif tipo == "separador":
                abertos[-1][3].append(y - 14)
                abertos[-1][7].append([y - 14 + 16, e[1], None])
                for k, v in abertos[-1][6].items():
                    pilhas[k] = list(v)
                y += 44
            elif tipo == "fim":
                q = abertos.pop()
                q[4] = y - 16
                if q[0] == "break":
                    # break: o operando encerra a interação. Fora dele o
                    # fluxo segue com as ativações de antes, e o quadro
                    # cobre todas as linhas de vida
                    for k, v in q[6].items():
                        pilhas[k] = list(v)
                    q[5].update(self.chaves)
                envolver(*q[5])
                y += 14
        fim_y = y
        for k in self.chaves:
            while pilhas[k]:
                barras.append((k, len(pilhas[k]) - 1, pilhas[k].pop(),
                               fim_y - 20))

        # quadros dos fragmentos: cobrem as linhas de vida envolvidas, com
        # margem maior para os de fora
        def profundidade(q):
            filhos = [f for f in quadros if f is not q and q[2] < f[2]
                      and f[4] < q[4]]
            return 1 + max((profundidade(f) for f in filhos), default=0)

        retas = []
        for q in quadros:
            pad = 14 + 12 * profundidade(q)
            xs = [self.cx[k] for k in q[5]]
            # as guardas ficam dentro do quadro
            xs += [self.cx[k] + BARRA + 4 + largura(g, 12) + 8 - pad
                   for _, g, k in q[7]]
            retas.append((min(xs) - pad, max(xs) + pad, q))

        larg_total = max([self.cx[k] + self.cab_w[k] / 2
                          for k in self.chaves] + [r[1] for r in retas])
        sd_w = larg_total + 24 - sd_x
        sd_h = fim_y + 6 - sd_y

        moldura(svg, sd_x, sd_y, sd_w, sd_h, "sd", self.nome)
        for k in self.chaves:
            x = self.cx[k]
            svg.add(f'<line x1="{x:.1f}" y1="{cabecas[k] + H_CABECA:.1f}" '
                    f'x2="{x:.1f}" y2="{fim_y - 10:.1f}" stroke="{TINTA}" '
                    f'stroke-width="1" stroke-dasharray="{TRACO}"/>')
        for k in self.chaves:
            w = self.cab_w[k]
            svg.retangulo(self.cx[k] - w / 2, cabecas[k], w, H_CABECA)
            svg.texto(self.cx[k], cabecas[k] + 23, self.rotulos[k], TAM_NOME,
                      "middle")
        for k, nivel, y0, y1 in sorted(barras, key=lambda b: b[1]):
            svg.retangulo(self.cx[k] - BARRA / 2 + nivel * BARRA / 2, y0,
                          BARRA, y1 - y0, espessura=1.1)
        # fragmentos sobre as barras, para o rótulo não ficar encoberto
        for x1, x2, q in retas:
            operador, _, y0, seps, y1 = q[:5]
            moldura(svg, x1, y0, x2 - x1, y1 - y0, operador)
            for ys in seps:
                svg.linha([(x1, ys), (x2, ys)], tracejado=True)
            for yg, g, k in q[7]:
                svg.texto(self.cx[k] + BARRA + 4, yg, g, 12, halo=True)
        for tipo, x1, x2, y, rot in mensagens:
            svg.linha([(x1, y), (x2, y)], tracejado=tipo != "chamada",
                      fim="seta_cheia" if tipo == "chamada" else "seta")
            svg.texto((x1 + x2) / 2, y - 7, rot, 12, "middle", halo=True)
        svg.salvar(arquivo, sd_x + sd_w + margem, sd_y + sd_h + margem)


# ------------------------------------------------- diagrama de comunicação


class Objeto(Caixa):
    """linha de vida no diagrama de comunicação: retângulo "nome : Tipo" """

    def __init__(self, rotulo):
        self.nome = rotulo
        self.w = max(110, largura(rotulo, TAM_NOME) + 24)
        self.h = H_CABECA

    def desenhar(self, svg):
        svg.retangulo(self.x, self.y, self.w, self.h)
        svg.texto(self.cx, self.y + 23, self.nome, TAM_NOME, "middle")


LH_MSG = 17


class Resposta(str):
    """mensagem de retorno (reply) em um diagrama de comunicação"""


def separar(mensagens):
    """(chamadas, respostas) de uma lista de mensagens"""
    return ([m for m in mensagens if not isinstance(m, Resposta)],
            [m for m in mensagens if isinstance(m, Resposta)])


def bloco_mensagens(mensagens):
    """largura e altura do bloco de mensagens de um lado da ligação"""
    if not mensagens:
        return 0, 0
    return (max(largura(m, 12) for m in mensagens),
            len(mensagens) * LH_MSG)


def ligacao(svg, a, b, mensagens=(), lado=1, x=None, y=None):
    """ligação reta (horizontal ou vertical) de a para b.
    As chamadas (enviadas de a para b) ficam do lado indicado, com uma seta
    cheia no sentido do envio. As respostas (Resposta, de b para a) ficam do
    outro lado, com uma seta tracejada no sentido contrário.
    Na horizontal, y é comum (padrão: centro de a), e as chamadas ficam
    acima (lado=1) ou abaixo (lado=-1).
    Na vertical, x é comum (padrão: centro de a), e as chamadas ficam à
    direita (lado=1) ou à esquerda (lado=-1).
    Devolve a caixa (x0, y0, x1, y1) ocupada pelas mensagens."""
    horizontal = a.base > b.topo and b.base > a.topo
    if horizontal:
        y = a.cy if y is None else y
        x1, x2 = (a.dir, b.esq) if a.cx < b.cx else (a.esq, b.dir)
        svg.linha([(x1, y), (x2, y)])
        return _rotular(svg, (x1, y), (x2, y), mensagens, lado)
    x = a.cx if x is None else x
    y1, y2 = (a.base, b.topo) if a.cy < b.cy else (a.topo, b.base)
    svg.linha([(x, y1), (x, y2)])
    return _rotular(svg, (x, y1), (x, y2), mensagens, lado)


def ligacao_rota(svg, pontos, mensagens=(), lado=1, trecho=None):
    """ligação em ângulos retos pelos pontos dados (do primeiro objeto ao
    segundo). As mensagens ficam no trecho indicado (padrão: o mais longo)"""
    svg.linha(pontos)
    if trecho is None:
        trecho = max(range(len(pontos) - 1), key=lambda i: abs(
            pontos[i + 1][0] - pontos[i][0]) + abs(pontos[i + 1][1] - pontos[i][1]))
    return _rotular(svg, pontos[trecho], pontos[trecho + 1], mensagens, lado)


def _rotular(svg, p1, p2, mensagens, lado):
    """chamadas e respostas, com as setas de sentido, sobre o trecho reto
    p1 -> p2"""
    chamadas, respostas = separar(mensagens)
    caixas = [_bloco(svg, p1, p2, chamadas, lado, False),
              _bloco(svg, p2, p1, respostas, -lado, True)]
    caixas = [c for c in caixas if c]
    if not caixas:
        return None
    return (min(c[0] for c in caixas), min(c[1] for c in caixas),
            max(c[2] for c in caixas), max(c[3] for c in caixas))


def _bloco(svg, p1, p2, mensagens, lado, resposta):
    """um bloco de mensagens no sentido p1 -> p2, do lado indicado (lado
    em relação ao sentido da chamada: acima/à direita = 1)"""
    if not mensagens:
        return None
    seta = dict(tracejado=resposta, fim="seta" if resposta else "seta_cheia")
    (x1, y1), (x2, y2) = p1, p2
    bw, bh = bloco_mensagens(mensagens)
    if y1 == y2:
        y = y1
        s = 1 if x2 > x1 else -1
        cx = (x1 + x2) / 2
        ys = y - 9 * lado
        svg.linha([(cx - s * 14, ys), (cx + s * 14, ys)], **seta)
        if lado == 1:
            base = ys - 10 - (len(mensagens) - 1) * LH_MSG
        else:
            base = ys + 18
        for i, m in enumerate(mensagens):
            svg.texto(cx - bw / 2, base + i * LH_MSG, m, 12, halo=True)
        return (cx - bw / 2, base - 13, cx + bw / 2,
                base + (len(mensagens) - 1) * LH_MSG + 4)
    x = x1
    s = 1 if y2 > y1 else -1
    cy = (y1 + y2) / 2
    xs = x + 9 * lado
    svg.linha([(xs, cy - s * 14), (xs, cy + s * 14)], **seta)
    y0 = cy - bh / 2 + 12
    for i, m in enumerate(mensagens):
        svg.texto(xs + 9 * lado, y0 + i * LH_MSG, m, 12,
                  "start" if lado == 1 else "end", halo=True)
    xt = xs + 9 * lado
    return (min(xt, xt + lado * bw), y0 - 13, max(xt, xt + lado * bw),
            y0 + bh - LH_MSG + 4)


def salvar_interacao(svg, caixas, nome, arquivo, margem=30, pad=24):
    """envolve o conteúdo de svg no quadro "sd nome". caixas são as (x0, y0,
    x1, y1) de tudo o que foi desenhado, em qualquer origem"""
    x0 = min(c[0] for c in caixas)
    y0 = min(c[1] for c in caixas)
    x1 = max(c[2] for c in caixas)
    y1 = max(c[3] for c in caixas)
    dx = margem + pad - x0
    dy = margem + H_PENTAGONO + pad - y0
    w = x1 - x0 + 2 * pad
    h = y1 - y0 + 2 * pad + H_PENTAGONO
    w = max(w, largura("sd " + nome, 13, True) + 60)
    final = Svg()
    moldura(final, margem, margem, w, h, "sd", nome)
    final.add(f'<g transform="translate({dx:.1f},{dy:.1f})">')
    final.partes += svg.partes
    final.add("</g>")
    final.salvar(arquivo, w + 2 * margem, h + 2 * margem)


def nota(svg, x, y, linhas, alvo=None):
    """comentário UML: retângulo com o canto dobrado, ligado ao elemento
    comentado (ponto alvo) por uma linha tracejada. Devolve a caixa"""
    w = max(largura(l, 12) for l in linhas) + 2 * PAD_X + 8
    h = len(linhas) * LH_MSG + 14
    if alvo:
        svg.linha([alvo, (x, y + h / 2) if alvo[0] < x else
                   (x + w, y + h / 2)], tracejado=True)
    d = 10
    svg.add(f'<path d="M{x:.1f},{y:.1f} H{x + w - d:.1f} L{x + w:.1f},'
            f'{y + d:.1f} V{y + h:.1f} H{x:.1f} Z M{x + w - d:.1f},{y:.1f} '
            f'V{y + d:.1f} H{x + w:.1f}" fill="#fff" stroke="{TINTA}" '
            f'stroke-width="1.2"/>')
    for i, l in enumerate(linhas):
        svg.texto(x + PAD_X, y + 7 + (i + 1) * LH_MSG - 4, l, 12)
    return (x, y, x + w, y + h)
