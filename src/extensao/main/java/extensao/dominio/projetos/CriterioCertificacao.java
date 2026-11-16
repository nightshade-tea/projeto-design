package extensao.dominio.projetos;

/** Critério de certificação; novos critérios são novas implementações (OCP). */
public interface CriterioCertificacao {

    boolean avaliar(ResumoFrequencia resumo);
}
