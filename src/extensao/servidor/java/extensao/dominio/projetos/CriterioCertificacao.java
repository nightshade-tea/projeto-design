package extensao.dominio.projetos;

/** Critério de certificação. Novos critérios são novas implementações (OCP). */
public interface CriterioCertificacao {

    boolean avaliar(ResumoFrequencia resumo);
}
