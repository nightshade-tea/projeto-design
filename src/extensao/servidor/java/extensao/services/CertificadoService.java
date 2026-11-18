package extensao.services;

import extensao.dominio.certificacao.Certificado;
import extensao.dominio.certificacao.CertificadoRepository;
import extensao.dominio.certificacao.GeradorDocumentoCertificado;
import extensao.dominio.identidade.Usuario;
import java.util.List;

/** RF08: listar e baixar os próprios certificados. */
public class CertificadoService {

    private final CertificadoRepository repository;
    private final GeradorDocumentoCertificado gerador;

    public CertificadoService(CertificadoRepository repository,
                              GeradorDocumentoCertificado gerador) {
        this.repository = repository;
        this.gerador = gerador;
    }

    public List<Certificado> listar(Usuario usuario) {
        return repository.listarPorAluno(Permissoes.exigirAluno(usuario));
    }

    /** Só entrega certificados que pertencem ao usuário. */
    public byte[] gerarArquivo(int id, Usuario usuario) {
        Certificado certificado = repository.buscarPorId(id)
                .orElseThrow(() -> new NaoEncontradoException("certificado não encontrado: " + id));
        if (!certificado.pertenceA(usuario)) {
            throw new SemPermissaoException("o certificado é de outro aluno");
        }
        return gerador.gerar(certificado);
    }
}
