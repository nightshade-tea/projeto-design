package extensao.dominio.projetos;

/** Operação recusada por uma regra de negócio (ex.: alterar um projeto encerrado). */
public class RegraNegocioException extends RuntimeException {

    public RegraNegocioException(String mensagem) {
        super(mensagem);
    }
}
