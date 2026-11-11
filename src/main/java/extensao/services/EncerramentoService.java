package extensao.services;

import extensao.dominio.certificacao.Certificado;
import extensao.dominio.certificacao.CertificadoRepository;
import extensao.dominio.identidade.Usuario;
import extensao.dominio.projetos.Projeto;
import extensao.dominio.projetos.ProjetoRepository;
import extensao.dominio.projetos.ResumoFrequencia;
import java.util.List;

/** RF07: encerra o projeto e emite um certificado para cada aluno aprovado. */
public class EncerramentoService {

    private final ProjetoRepository projetos;
    private final CertificadoRepository certificados;

    public EncerramentoService(ProjetoRepository projetos, CertificadoRepository certificados) {
        this.projetos = projetos;
        this.certificados = certificados;
    }

    /** Devolve os certificados emitidos. */
    public List<Certificado> encerrar(int id, Usuario usuario) {
        Projeto projeto = projetos.buscarPorId(id)
                .orElseThrow(() -> new NaoEncontradoException("projeto não encontrado: " + id));
        Permissoes.exigirGestor(projeto, usuario);
        projeto.encerrar();
        List<ResumoFrequencia> aprovados = projeto.aprovados();
        projetos.salvar(projeto);
        return aprovados.stream()
                .filter(resumo -> !temCertificado(resumo))
                .map(resumo -> {
                    Certificado certificado = new Certificado(resumo);
                    certificados.salvar(certificado);
                    return certificado;
                })
                .toList();
    }

    /** No máximo um certificado por aluno e projeto. */
    private boolean temCertificado(ResumoFrequencia resumo) {
        return certificados.listarPorAluno(resumo.getAluno()).stream()
                .anyMatch(c -> c.getProjeto().getId().equals(resumo.getProjeto().getId()));
    }
}
