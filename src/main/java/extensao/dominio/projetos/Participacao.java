package extensao.dominio.projetos;

import extensao.dominio.identidade.Aluno;
import java.time.LocalDate;
import java.util.List;

/** Vínculo de um aluno com um projeto, de inicio até fim (inclusive). */
public class Participacao {

    private final Aluno aluno;
    private final LocalDate inicio;
    private LocalDate fim;

    public Participacao(Aluno aluno, LocalDate inicio, LocalDate fim) {
        this.aluno = aluno;
        this.inicio = inicio;
        this.fim = fim;
    }

    /** Desvincular só encerra a participação; as presenças continuam valendo. */
    public void encerrar() {
        if (fim == null) {
            fim = LocalDate.now();
        }
    }

    public boolean ativaEm(LocalDate data) {
        return !data.isBefore(inicio) && (fim == null || !data.isAfter(fim));
    }

    public boolean encerrada() {
        return fim != null;
    }

    /** Considera só as atividades dentro do período da participação. */
    public ResumoFrequencia resumoFrequencia(Projeto projeto, List<Atividade> atividades) {
        int horas = 0;
        int presencas = 0;
        int total = 0;
        for (Atividade atividade : atividades) {
            if (!ativaEm(atividade.getData())) {
                continue;
            }
            total++;
            if (atividade.estevePresente(aluno)) {
                presencas++;
                horas += atividade.getCargaHoraria();
            }
        }
        return new ResumoFrequencia(aluno, projeto, horas, presencas, total);
    }

    public Aluno getAluno() {
        return aluno;
    }

    public LocalDate getInicio() {
        return inicio;
    }

    public LocalDate getFim() {
        return fim;
    }
}
