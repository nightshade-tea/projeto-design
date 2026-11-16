package extensao.services;

import extensao.dominio.identidade.Administrador;
import extensao.dominio.identidade.Aluno;
import extensao.dominio.identidade.Usuario;
import extensao.dominio.projetos.Projeto;

/** Regras de permissão comuns aos services (RN02 e RN03). */
final class Permissoes {

    private Permissoes() {
    }

    /** O professor só gerencia projetos que coordena; o administrador gerencia qualquer um. */
    static void exigirGestor(Projeto projeto, Usuario usuario) {
        if (!projeto.getCoordenador().mesmoQue(usuario) && !(usuario instanceof Administrador)) {
            throw new SemPermissaoException("só o coordenador ou um administrador gerencia o projeto");
        }
    }

    static Aluno exigirAluno(Usuario usuario) {
        if (usuario instanceof Aluno aluno) {
            return aluno;
        }
        throw new SemPermissaoException("só alunos têm horas e certificados");
    }
}
