package extensao.dominio.identidade;

import java.util.Optional;

/**
 * Isola o login institucional (ASR02). Implementações:
 * ProvedorIdentidadeInstitucional (produção) e ProvedorIdentidadeTeste.
 */
public interface ProvedorIdentidade {

    /** Valida o token do login institucional, ou devolve vazio se for inválido. */
    Optional<Usuario> identificar(String token);

    /** Busca um usuário pela matrícula, ou devolve vazio se não existir. */
    Optional<Usuario> buscarPorMatricula(String matricula);

    /** Endereço da página de login institucional. */
    String urlLogin();
}
