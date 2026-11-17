package extensao.dominio.projetos;

import extensao.dominio.identidade.Aluno;

/** Frequência de um aluno em um projeto; usado na consulta de horas e na emissão de certificados. */
public class ResumoFrequencia {

    private final Aluno aluno;
    private final Projeto projeto;
    private final int horasCumpridas;
    private final int qtdPresencas;
    private final int qtdAtividades;

    public ResumoFrequencia(Aluno aluno, Projeto projeto, int horasCumpridas, int qtdPresencas,
                            int qtdAtividades) {
        this.aluno = aluno;
        this.projeto = projeto;
        this.horasCumpridas = horasCumpridas;
        this.qtdPresencas = qtdPresencas;
        this.qtdAtividades = qtdAtividades;
    }

    /** Percentual de 0 a 100; sem atividades, 0. */
    public double percentualPresenca() {
        return qtdAtividades == 0 ? 0 : 100.0 * qtdPresencas / qtdAtividades;
    }

    public Aluno getAluno() {
        return aluno;
    }

    public Projeto getProjeto() {
        return projeto;
    }

    public int getHorasCumpridas() {
        return horasCumpridas;
    }

    public int getQtdPresencas() {
        return qtdPresencas;
    }

    public int getQtdAtividades() {
        return qtdAtividades;
    }
}
