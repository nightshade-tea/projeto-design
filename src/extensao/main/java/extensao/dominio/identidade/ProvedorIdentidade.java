package extensao.dominio.identidade;

import java.util.Optional;

/**
 * Isola o login institucional (ASR02). Implementações:
 * ProvedorIdentidadeInstitucional (produção) e ProvedorIdentidadeTeste.
 */
public interface ProvedorIdentidade {

    /** Valida o token do login institucional; vazio se o token for inválido. */
    Optional<Usuario> identificar(String token);

    /** Busca um usuário pela matrícula; vazio se não existir. */
    Optional<Usuario> buscarPorMatricula(String matricula);

    /** Endereço da página de login institucional. */
    String urlLogin();
}
