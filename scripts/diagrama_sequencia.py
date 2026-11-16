#!/usr/bin/env python3
# Gera os diagramas de sequência (ver docs/arquitetura.md e docs/dominio.md):
# - docs/diagramas/sequencia.svg: cenário completo, com
#   autenticação: o professor faz login pelo login institucional, cria um
#   projeto e vincula um aluno (sem o caso de token inválido)
# e um diagrama por caso de uso, começando pela identificação do usuário:
# - docs/diagramas/sequencia/login.svg
# - docs/diagramas/sequencia/criar_projeto.svg (RF01)
# - docs/diagramas/sequencia/vincular_aluno.svg (RF03)
# - docs/diagramas/sequencia/registrar_presenca.svg (RF04)
# - docs/diagramas/sequencia/consultar_horas.svg (RF05, horas do aluno)
# - docs/diagramas/sequencia/consultar_horas_projeto.svg (RF05, horas dos
#   participantes, para o coordenador)
# - docs/diagramas/sequencia/encerrar_projeto.svg (RF07)
# - docs/diagramas/sequencia/baixar_certificado.svg (RF08)
# Uso: python3 scripts/diagrama_sequencia.py
#
# A validação do token no login institucional (validar(token)) aparece no
# login e no cenário completo, e o 401 só no login; nos diagramas por caso de uso,
# identificar(token) devolve o usuário direto, para não repetir esse trecho.
# As recusas por permissão (403), recurso inexistente (404) e regra de
# negócio (409) aparecem como fragmentos break.
#
# Notação UML 2:
# - linhas de vida "nome : Tipo", sem sublinhado
# - chamadas síncronas com seta cheia, retornos tracejados com seta aberta;
#   o rótulo do retorno é "alvo = operacao()" ou "operacao(): valor"
#   (reply-message-label, UML 2.5.1, 17.4.4.1)
# - criação de objeto com seta tracejada até a cabeça da linha de vida
# - fragmentos combinados loop, opt e break; a guarda é uma condição, sobre a
#   linha de vida que envia a primeira mensagem do fragmento
from uml import Sequencia


def identificar(ctrl, ext=False):
    """cada requisição começa identificando o usuário pelo token; com ext, o
    provedor valida o token no login institucional"""
    s.chamada(ctrl, "auth", "identificar(token)")
    s.chamada("auth", "idp", "identificar(token)")
    if ext:
        s.chamada("idp", "ext", "validar(token)")
        s.retorno("ext", "idp", "matricula")
    s.retorno("idp", "auth", "usuario")
    s.retorno("auth", ctrl, "usuario")


AUTH = [("auth", ": AutenticacaoService"), ("idp", ": ProvedorIdentidade")]


def recusa(svc, ctrl, guarda, motivo, status):
    """break: o service recusa a requisição e o controller responde com o
    status de erro; a interação termina"""
    s.inicio("break", guarda)
    s.retorno(svc, ctrl, valor=motivo)
    s.retorno(ctrl, "cliente", valor=status)
    s.fim()


def gerenciar(svc, ctrl, projeto="projeto"):
    """RN02/RN03: só o coordenador ou um administrador gerencia o projeto,
    e um projeto encerrado não aceita alterações"""
    s.chamada(svc, projeto, "podeGerenciar(usuario)")
    s.retorno(projeto, svc, "pode")
    recusa(svc, ctrl, "[não pode]", "sem permissão", "403 Forbidden")
    recusa(svc, ctrl, "[projeto encerrado]", "projeto encerrado",
           "409 Conflict")


def buscar_aluno(svc, ctrl):
    """busca pela matrícula; a matrícula precisa ser de um Aluno"""
    s.chamada(svc, "idp", "buscarPorMatricula(matricula)")
    s.retorno("idp", svc, "aluno")
    recusa(svc, ctrl, "[matricula não é de um Aluno]", "não é aluno", "409 Conflict")


def criar(ctrl):
    s.chamada("cliente", ctrl, "criar(token, titulo, descricao)")
    identificar(ctrl, ext=ctrl == "pctrl")
    s.chamada(ctrl, "svc", "criar(titulo, descricao, usuario)")
    recusa("svc", ctrl, "[usuario não é Professor nem Administrador]",
           "sem permissão", "403 Forbidden")
    s.criacao("svc", "projeto", "Projeto(titulo, descricao, coordenador)")
    s.chamada("svc", "repo", "salvar(projeto)")
    s.retorno("repo", "svc")
    s.retorno("svc", ctrl, "projeto")
    s.retorno(ctrl, "cliente", valor="202 Accepted")


def vincular(ctrl):
    s.chamada("cliente", ctrl, "vincular(token, id, matricula)")
    identificar(ctrl, ext=ctrl == "pctrl")
    s.chamada(ctrl, "svc", "vincular(id, matricula, usuario)")
    s.chamada("svc", "repo", "buscarPorId(id)")
    s.retorno("repo", "svc", "projeto")
    gerenciar("svc", ctrl)
    buscar_aluno("svc", ctrl)
    s.chamada("svc", "projeto", "vincular(aluno)")
    s.retorno("projeto", "svc")
    s.chamada("svc", "repo", "salvar(projeto)")
    s.retorno("repo", "svc")
    s.retorno("svc", ctrl)
    s.retorno(ctrl, "cliente", valor="202 Accepted")


# --------------------------------------------------- criar projeto (RF01)

s = Sequencia("Criar projeto", [
    ("cliente", ": Cliente web"),
    ("ctrl", ": ProjetoController"), *AUTH,
    ("svc", ": ProjetoService"),
    ("projeto", "projeto : Projeto"),
    ("repo", ": ProjetoRepository"),
])
criar("ctrl")
s.desenhar("sequencia/criar_projeto.svg")

# -------------------------------------------------- vincular aluno (RF03)

s = Sequencia("Vincular aluno", [
    ("cliente", ": Cliente web"),
    ("ctrl", ": ProjetoController"), *AUTH,
    ("svc", ": ProjetoService"),
    ("repo", ": ProjetoRepository"),
    ("projeto", "projeto : Projeto"),
])
vincular("ctrl")
s.desenhar("sequencia/vincular_aluno.svg")

# ---------------------------------------------- registrar presença (RF04)

s = Sequencia("Registrar presença", [
    ("cliente", ": Cliente web"),
    ("ctrl", ": FrequenciaController"), *AUTH,
    ("svc", ": FrequenciaService"),
    ("repo", ": ProjetoRepository"),
    ("projeto", "projeto : Projeto"),
])
s.chamada("cliente", "ctrl",
          "registrarPresenca(token, id, atividadeId, matricula)")
identificar("ctrl")
s.chamada("ctrl", "svc",
          "registrarPresenca(id, atividadeId, matricula, usuario)")
s.chamada("svc", "repo", "buscarPorId(id)")
s.retorno("repo", "svc", "projeto")
gerenciar("svc", "ctrl")
s.chamada("svc", "projeto", "atividade(atividadeId)")
s.retorno("projeto", "svc", "atividade")
buscar_aluno("svc", "ctrl")
s.chamada("svc", "projeto", "registrarPresenca(atividade, aluno)")
s.retorno("projeto", "svc")
s.chamada("svc", "repo", "salvar(projeto)")
s.retorno("repo", "svc")
s.retorno("svc", "ctrl")
s.retorno("ctrl", "cliente", valor="202 Accepted")
s.desenhar("sequencia/registrar_presenca.svg")

# ------------------------------------------------ encerrar projeto (RF07)

s = Sequencia("Encerrar projeto", [
    ("cliente", ": Cliente web"),
    ("ctrl", ": ProjetoController"), *AUTH,
    ("svc", ": EncerramentoService"),
    ("prepo", ": ProjetoRepository"),
    ("projeto", "projeto : Projeto"),
    ("cert", "certificado : Certificado"),
    ("crepo", ": CertificadoRepository"),
])
s.chamada("cliente", "ctrl", "encerrar(token, id)")
identificar("ctrl")
s.chamada("ctrl", "svc", "encerrar(id, usuario)")
s.chamada("svc", "prepo", "buscarPorId(id)")
s.retorno("prepo", "svc", "projeto")
gerenciar("svc", "ctrl")
s.chamada("svc", "projeto", "encerrar()")
s.retorno("projeto", "svc")
s.chamada("svc", "projeto", "aprovados()")
s.retorno("projeto", "svc", "aprovados")
s.chamada("svc", "prepo", "salvar(projeto)")
s.retorno("prepo", "svc")
# no máximo um certificado por aluno e projeto (a emissão pode ser repetida)
s.inicio("loop", "[para cada resumo em aprovados]")
s.chamada("svc", "crepo", "existe(projeto, resumo.aluno)")
s.retorno("crepo", "svc", "existe")
s.inicio("opt", "[não existe]")
s.criacao("svc", "cert", "Certificado(resumo)")
s.chamada("svc", "crepo", "salvar(certificado)")
s.retorno("crepo", "svc")
s.fim()
s.fim()
s.retorno("svc", "ctrl")
s.retorno("ctrl", "cliente", valor="202 Accepted")
s.desenhar("sequencia/encerrar_projeto.svg")

# ------------------------------------------ consultar horas do aluno (RF05)

s = Sequencia("Consultar horas", [
    ("cliente", ": Cliente web"),
    ("ctrl", ": FrequenciaController"), *AUTH,
    ("svc", ": FrequenciaService"),
    ("repo", ": ProjetoRepository"),
    ("projeto", "projeto : Projeto"),
])
s.chamada("cliente", "ctrl", "consultarHoras(token)")
identificar("ctrl")
s.chamada("ctrl", "svc", "consultarHoras(usuario)")
recusa("svc", "ctrl", "[usuario não é Aluno]", "sem permissão",
       "403 Forbidden")
s.chamada("svc", "repo", "listarPorAluno(usuario)")
s.retorno("repo", "svc", "projetos")
s.inicio("loop", "[para cada projeto em projetos]")
s.chamada("svc", "projeto", "resumoFrequencia(usuario)")
s.retorno("projeto", "svc", "resumo")
s.fim()
# o total é a soma de horasCumpridas dos resumos, feita no service
s.retorno("svc", "ctrl", "resumos")
s.retorno("ctrl", "cliente", valor="200 OK")
s.desenhar("sequencia/consultar_horas.svg")

# ------------------------- consultar horas dos participantes (RF05, coordenador)

s = Sequencia("Consultar horas dos participantes", [
    ("cliente", ": Cliente web"),
    ("ctrl", ": FrequenciaController"), *AUTH,
    ("svc", ": FrequenciaService"),
    ("repo", ": ProjetoRepository"),
    ("projeto", "projeto : Projeto"),
])
s.chamada("cliente", "ctrl", "consultarHorasProjeto(token, id)")
identificar("ctrl")
s.chamada("ctrl", "svc", "consultarHorasProjeto(id, usuario)")
s.chamada("svc", "repo", "buscarPorId(id)")
s.retorno("repo", "svc", "projeto")
s.chamada("svc", "projeto", "podeGerenciar(usuario)")
s.retorno("projeto", "svc", "pode")
recusa("svc", "ctrl", "[não pode]", "sem permissão", "403 Forbidden")
s.chamada("svc", "projeto", "resumos()")
s.retorno("projeto", "svc", "resumos")
s.retorno("svc", "ctrl", "resumos")
s.retorno("ctrl", "cliente", valor="200 OK")
s.desenhar("sequencia/consultar_horas_projeto.svg")

# ---------------------------------------------- baixar certificado (RF08)

s = Sequencia("Baixar certificado", [
    ("cliente", ": Cliente web"),
    ("ctrl", ": CertificadoController"), *AUTH,
    ("svc", ": CertificadoService"),
    ("repo", ": CertificadoRepository"),
    ("cert", "certificado : Certificado"),
    ("ger", ": GeradorDocumentoCertificado"),
])
s.chamada("cliente", "ctrl", "baixar(token, id)")
identificar("ctrl")
s.chamada("ctrl", "svc", "gerarArquivo(id, usuario)")
s.chamada("svc", "repo", "buscarPorId(id)")
s.retorno("repo", "svc", "certificado")
recusa("svc", "ctrl", "[certificado não encontrado]", "não encontrado",
       "404 Not Found")
s.chamada("svc", "cert", "pertenceA(usuario)")
s.retorno("cert", "svc", "pertence")
recusa("svc", "ctrl", "[não pertence]", "sem permissão", "403 Forbidden")
s.chamada("svc", "ger", "gerar(certificado)")
s.retorno("ger", "svc", "arquivo")
s.retorno("svc", "ctrl", "arquivo")
s.retorno("ctrl", "cliente", valor="200 OK (PDF)")
s.desenhar("sequencia/baixar_certificado.svg")

# ----------------------------------------------------------------- login

s = Sequencia("Login", [
    ("cliente", ": Cliente web"),
    ("ext", ": Login institucional"),
    ("ctrl", ": AutenticacaoController"), *AUTH,
])
# o servidor redireciona para o login institucional (sistema externo)
s.chamada("cliente", "ctrl", "login()")
s.chamada("ctrl", "auth", "urlLogin()")
s.chamada("auth", "idp", "urlLogin()")
s.retorno("idp", "auth", "url")
s.retorno("auth", "ctrl", "url")
s.retorno("ctrl", "cliente", valor="302 Found (url)")
s.chamada("cliente", "ext", "entrar(matricula, senha)")
s.retorno("ext", "cliente", valor="302 Found (token)")
# usuário logado; o token é validado no login institucional
s.chamada("cliente", "ctrl", "consultarUsuario(token)")
s.chamada("ctrl", "auth", "identificar(token)")
s.chamada("auth", "idp", "identificar(token)")
s.chamada("idp", "ext", "validar(token)")
s.inicio("break", "[token inválido]")
s.retorno("ext", "idp", valor="token inválido")
s.retorno("idp", "auth", valor="token inválido")
s.retorno("auth", "ctrl", valor="token inválido")
s.retorno("ctrl", "cliente", valor="401 Unauthorized")
s.fim()
s.retorno("ext", "idp", "matricula")
s.retorno("idp", "auth", "usuario")
s.retorno("auth", "ctrl", "usuario")
s.retorno("ctrl", "cliente", valor="200 OK (nome, papel)")
s.desenhar("sequencia/login.svg")

# ------------------------------------- cenário completo, com autenticação

s = Sequencia("Professor cria projeto e vincula aluno", [
    ("cliente", ": Cliente web"),
    ("ext", ": Login institucional"),
    ("actrl", ": AutenticacaoController"),
    ("pctrl", ": ProjetoController"),
    ("auth", ": AutenticacaoService"),
    ("idp", ": ProvedorIdentidade"),
    ("svc", ": ProjetoService"),
    ("repo", ": ProjetoRepository"),
    ("projeto", "projeto : Projeto"),
])
# login: o servidor redireciona para o login institucional (sistema externo)
s.chamada("cliente", "actrl", "login()")
s.chamada("actrl", "auth", "urlLogin()")
s.chamada("auth", "idp", "urlLogin()")
s.retorno("idp", "auth", "url")
s.retorno("auth", "actrl", "url")
s.retorno("actrl", "cliente", valor="302 Found (url)")
s.chamada("cliente", "ext", "entrar(matricula, senha)")
s.retorno("ext", "cliente", valor="302 Found (token)")
# usuário logado; o token é validado no login institucional
s.chamada("cliente", "actrl", "consultarUsuario(token)")
s.chamada("actrl", "auth", "identificar(token)")
s.chamada("auth", "idp", "identificar(token)")
s.chamada("idp", "ext", "validar(token)")
s.retorno("ext", "idp", "matricula")
s.retorno("idp", "auth", "usuario")
s.retorno("auth", "actrl", "usuario")
s.retorno("actrl", "cliente", valor="200 OK (nome, papel)")
# criar projeto
criar("pctrl")
# vincular aluno
vincular("pctrl")
s.desenhar("sequencia.svg")
