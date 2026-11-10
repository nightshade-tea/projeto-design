package extensao.dominio.certificacao;

import extensao.dominio.identidade.Aluno;
import java.util.List;
import java.util.Optional;

/** Salva e busca o agregado Certificado; a implementação fica fora do domínio. */
public interface CertificadoRepository {

    /** Salva o certificado; um certificado sem id recebe um id novo. */
    void salvar(Certificado certificado);

    Optional<Certificado> buscarPorId(int id);

    List<Certificado> listarPorAluno(Aluno aluno);
}
