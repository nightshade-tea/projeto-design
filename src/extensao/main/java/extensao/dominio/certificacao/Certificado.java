package extensao.dominio.certificacao;

import extensao.dominio.identidade.Aluno;
import extensao.dominio.identidade.Usuario;
import extensao.dominio.projetos.Projeto;
import extensao.dominio.projetos.ResumoFrequencia;
import java.time.LocalDateTime;

/**
 * Certificado emitido para um aluno aprovado. Guarda uma cópia dos dados do
 * momento da emissão, então alterações posteriores no projeto não o mudam.
 */
public class Certificado {

    private Integer id;
    private final Projeto projeto;
    private final Aluno aluno;
    private final String nomeAluno;
    private final String tituloProjeto;
    private final String nomeCoordenador;
    private final int cargaHoraria;
    private final LocalDateTime emitidoEm;

    public Certificado(ResumoFrequencia resumo) {
        this(null, resumo.getProjeto(), resumo.getAluno(), resumo.getAluno().getNome(),
                resumo.getProjeto().getTitulo(), resumo.getProjeto().getCoordenador().getNome(),
                resumo.getHorasCumpridas(), LocalDateTime.now());
    }

    private Certificado(Integer id, Projeto projeto, Aluno aluno, String nomeAluno,
                        String tituloProjeto, String nomeCoordenador, int cargaHoraria,
                        LocalDateTime emitidoEm) {
        this.id = id;
        this.projeto = projeto;
        this.aluno = aluno;
        this.nomeAluno = nomeAluno;
        this.tituloProjeto = tituloProjeto;
        this.nomeCoordenador = nomeCoordenador;
        this.cargaHoraria = cargaHoraria;
        this.emitidoEm = emitidoEm;
    }

    /** Recria um certificado já salvo; usado só pelas implementações dos repositories. */
    public static Certificado restaurar(Integer id, Projeto projeto, Aluno aluno, String nomeAluno,
                                        String tituloProjeto, String nomeCoordenador,
                                        int cargaHoraria, LocalDateTime emitidoEm) {
        return new Certificado(id, projeto, aluno, nomeAluno, tituloProjeto, nomeCoordenador,
                cargaHoraria, emitidoEm);
    }

    public boolean pertenceA(Usuario usuario) {
        return aluno.mesmoQue(usuario);
    }

    /** O id é atribuído pelo repository ao salvar um certificado novo. */
    public void atribuirId(int id) {
        if (this.id != null) {
            throw new IllegalStateException("o certificado já tem id");
        }
        this.id = id;
    }

    public Integer getId() {
        return id;
    }

    public Projeto getProjeto() {
        return projeto;
    }

    public Aluno getAluno() {
        return aluno;
    }

    public String getNomeAluno() {
        return nomeAluno;
    }

    public String getTituloProjeto() {
        return tituloProjeto;
    }

    public String getNomeCoordenador() {
        return nomeCoordenador;
    }

    public int getCargaHoraria() {
        return cargaHoraria;
    }

    public LocalDateTime getEmitidoEm() {
        return emitidoEm;
    }
}
