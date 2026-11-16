package extensao.dominio.projetos;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/** Conjunto de critérios de um projeto; o resumo precisa atender a todos. */
public class CriteriosCertificacao {

    private final List<CriterioCertificacao> criterios = new ArrayList<>();

    CriteriosCertificacao(List<CriterioCertificacao> criterios) {
        definir(criterios);
    }

    /** Substitui os critérios. */
    public void definir(List<CriterioCertificacao> criterios) {
        this.criterios.clear();
        this.criterios.addAll(criterios);
    }

    /** Sem critérios definidos, nenhum resumo atende. */
    public boolean atende(ResumoFrequencia resumo) {
        return !criterios.isEmpty() && criterios.stream().allMatch(c -> c.avaliar(resumo));
    }

    public List<CriterioCertificacao> getCriterios() {
        return Collections.unmodifiableList(criterios);
    }
}
