#!/usr/bin/env python3
# Gera os diagramas de sequência (ver docs/arquitetura.md e docs/dominio.md):
# - docs/diagramas/sequencia.svg: cenário completo, com
#   autenticação: o professor faz login pelo login institucional, cria um
#   projeto e vincula um aluno; se o token for inválido, a
#   interação termina com 401 (fragmento break)
# e um diagrama por caso de uso, começando pela identificação do usuário:
# - docs/diagramas/sequencia/login.svg
# - docs/diagramas/sequencia/criar_projeto.svg (RF01)
# - docs/diagramas/sequencia/vincular_aluno.svg (RF03)
# - docs/diagramas/sequencia/registrar_presenca.svg (RF04)
# - docs/diagramas/sequencia/consultar_horas.svg (RF05)
# - docs/diagramas/sequencia/encerrar_projeto.svg (RF07)
# - docs/diagramas/sequencia/baixar_certificado.svg (RF08)
# Uso: python3 scripts/diagrama_sequencia.py
#
# Notação UML 2:
# - linhas de vida "nome : Tipo", sem sublinhado
# - chamadas síncronas com seta cheia, retornos tracejados com seta aberta
# - criação de objeto com seta tracejada até a cabeça da linha de vida
# - fragmentos combinados loop e break; a guarda é uma condição, sobre a linha de
#   vida que envia a primeira mensagem do loop
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

# --------------------------------------------------- criar projeto (RF01)

s = Sequencia("Criar projeto", [
    ("cliente", ": Cliente web"),
    ("ctrl", ": ProjetoController"), *AUTH,
    ("svc", ": ProjetoService"),
    ("projeto", "projeto : Projeto"),
    ("repo", ": ProjetoRepository"),
])
s.chamada("cliente", "ctrl", "criar(token, titulo, descricao)")
identificar("ctrl")
s.chamada("ctrl", "svc", "criar(titulo, descricao, usuario)")
s.criacao("svc", "projeto", "Projeto(titulo, descricao, coordenador)")
s.chamada("svc", "repo", "salvar(projeto)")
s.retorno("repo", "svc")
s.retorno("svc", "ctrl", "projeto")
s.retorno("ctrl", "cliente", "202 Accepted")
s.desenhar("sequencia/criar_projeto.svg")

# -------------------------------------------------- vincular aluno (RF03)

s = Sequencia("Vincular aluno", [
    ("cliente", ": Cliente web"),
    ("ctrl", ": ProjetoController"), *AUTH,
    ("svc", ": ProjetoService"),
    ("repo", ": ProjetoRepository"),
    ("projeto", "projeto : Projeto"),
])
s.chamada("cliente", "ctrl", "vincular(token, id, matricula)")
identificar("ctrl")
s.chamada("ctrl", "svc", "vincular(id, matricula, usuario)")
s.chamada("svc", "repo", "buscarPorId(id)")
s.retorno("repo", "svc", "projeto")
s.chamada("svc", "idp", "buscarPorMatricula(matricula)")
s.retorno("idp", "svc", "aluno")
s.chamada("svc", "projeto", "vincular(aluno)")
s.retorno("projeto", "svc")
s.chamada("svc", "repo", "salvar(projeto)")
s.retorno("repo", "svc")
s.retorno("svc", "ctrl")
s.retorno("ctrl", "cliente", "202 Accepted")
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
s.chamada("svc", "idp", "buscarPorMatricula(matricula)")
s.retorno("idp", "svc", "aluno")
s.chamada("svc", "projeto", "registrarPresenca(atividade, aluno)")
s.retorno("projeto", "svc")
s.chamada("svc", "repo", "salvar(projeto)")
s.retorno("repo", "svc")
s.retorno("svc", "ctrl")
s.retorno("ctrl", "cliente", "202 Accepted")
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
s.chamada("svc", "projeto", "encerrar()")
s.retorno("projeto", "svc")
s.chamada("svc", "projeto", "aprovados()")
s.retorno("projeto", "svc", "aprovados")
s.chamada("svc", "prepo", "salvar(projeto)")
s.retorno("prepo", "svc")
s.inicio("loop", "[há resumo em aprovados sem certificado]")
s.criacao("svc", "cert", "Certificado(resumo)")
s.chamada("svc", "crepo", "salvar(certificado)")
s.retorno("crepo", "svc")
s.fim()
s.retorno("svc", "ctrl")
s.retorno("ctrl", "cliente", "202 Accepted")
s.desenhar("sequencia/encerrar_projeto.svg")

# ------------------------------------------------- consultar horas (RF05)

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
s.chamada("svc", "repo", "listarPorAluno(aluno)")
s.retorno("repo", "svc", "projetos")
s.inicio("loop", "[há projeto em projetos sem resumo]")
s.chamada("svc", "projeto", "resumoFrequencia(aluno)")
s.retorno("projeto", "svc", "resumo")
s.fim()
s.retorno("svc", "ctrl", "resumos")
s.retorno("ctrl", "cliente", "200 OK")
s.desenhar("sequencia/consultar_horas.svg")

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
s.chamada("svc", "cert", "pertenceA(usuario)")
s.retorno("cert", "svc", "true")
s.chamada("svc", "ger", "gerar(certificado)")
s.retorno("ger", "svc", "arquivo")
s.retorno("svc", "ctrl", "arquivo")
s.retorno("ctrl", "cliente", "200 OK (PDF)")
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
s.retorno("ctrl", "cliente", "302 Found (url)")
s.chamada("cliente", "ext", "entrar(matricula, senha)")
s.retorno("ext", "cliente", "302 Found (token)")
# usuário logado; o token é validado no login institucional
s.chamada("cliente", "ctrl", "consultarUsuario(token)")
s.chamada("ctrl", "auth", "identificar(token)")
s.chamada("auth", "idp", "identificar(token)")
s.chamada("idp", "ext", "validar(token)")
s.inicio("break", "[token inválido]")
s.retorno("ext", "idp", "token inválido")
s.retorno("idp", "auth", "token inválido")
s.retorno("auth", "ctrl", "token inválido")
s.retorno("ctrl", "cliente", "401 Unauthorized")
s.fim()
s.retorno("ext", "idp", "matricula")
s.retorno("idp", "auth", "usuario")
s.retorno("auth", "ctrl", "usuario")
s.retorno("ctrl", "cliente", "200 OK (nome, papel)")
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
s.retorno("actrl", "cliente", "302 Found (url)")
s.chamada("cliente", "ext", "entrar(matricula, senha)")
s.retorno("ext", "cliente", "302 Found (token)")
# usuário logado; o token é validado no login institucional
s.chamada("cliente", "actrl", "consultarUsuario(token)")
s.chamada("actrl", "auth", "identificar(token)")
s.chamada("auth", "idp", "identificar(token)")
s.chamada("idp", "ext", "validar(token)")
s.inicio("break", "[token inválido]")
s.retorno("ext", "idp", "token inválido")
s.retorno("idp", "auth", "token inválido")
s.retorno("auth", "actrl", "token inválido")
s.retorno("actrl", "cliente", "401 Unauthorized")
s.fim()
s.retorno("ext", "idp", "matricula")
s.retorno("idp", "auth", "usuario")
s.retorno("auth", "actrl", "usuario")
s.retorno("actrl", "cliente", "200 OK (nome, papel)")
# criar projeto
s.chamada("cliente", "pctrl", "criar(token, titulo, descricao)")
identificar("pctrl", ext=True)
s.chamada("pctrl", "svc", "criar(titulo, descricao, usuario)")
s.criacao("svc", "projeto", "Projeto(titulo, descricao, coordenador)")
s.chamada("svc", "repo", "salvar(projeto)")
s.retorno("repo", "svc")
s.retorno("svc", "pctrl", "projeto")
s.retorno("pctrl", "cliente", "202 Accepted")
# vincular aluno
s.chamada("cliente", "pctrl", "vincular(token, id, matricula)")
identificar("pctrl", ext=True)
s.chamada("pctrl", "svc", "vincular(id, matricula, usuario)")
s.chamada("svc", "repo", "buscarPorId(id)")
s.retorno("repo", "svc", "projeto")
s.chamada("svc", "idp", "buscarPorMatricula(matricula)")
s.retorno("idp", "svc", "aluno")
s.chamada("svc", "projeto", "vincular(aluno)")
s.retorno("projeto", "svc")
s.chamada("svc", "repo", "salvar(projeto)")
s.retorno("repo", "svc")
s.retorno("svc", "pctrl")
s.retorno("pctrl", "cliente", "202 Accepted")
s.desenhar("sequencia.svg")
