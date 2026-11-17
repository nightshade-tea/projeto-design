package extensao.services;

/** O usuário não tem permissão para a operação (403). */
public class SemPermissaoException extends RuntimeException {

    public SemPermissaoException(String mensagem) {
        super(mensagem);
    }
}
