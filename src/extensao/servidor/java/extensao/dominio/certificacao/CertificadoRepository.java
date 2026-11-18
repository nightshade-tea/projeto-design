package extensao.dominio.certificacao;

import extensao.dominio.identidade.Aluno;
import extensao.dominio.projetos.Projeto;
import java.util.List;
import java.util.Optional;

/** Salva e busca o agregado Certificado. A implementação fica fora do domínio. */
public interface CertificadoRepository {

    /** Salva o certificado. Um certificado sem id recebe um id novo. */
    void salvar(Certificado certificado);

    Optional<Certificado> buscarPorId(int id);

    List<Certificado> listarPorAluno(Aluno aluno);

    /** Se o aluno já tem certificado do projeto, para a emissão não duplicar certificados. */
    boolean existe(Projeto projeto, Aluno aluno);
}
