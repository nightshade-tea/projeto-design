package extensao.dominio.projetos;

import java.math.BigDecimal;

public class PercentualMinimoPresenca implements CriterioCertificacao {

    private final double pct;

    public PercentualMinimoPresenca(double pct) {
        if (pct <= 0 || pct > 100) {
            throw new IllegalArgumentException("o percentual deve estar entre 0 e 100");
        }
        this.pct = pct;
    }

    @Override
    public boolean avaliar(ResumoFrequencia resumo) {
        return resumo.percentualPresenca() >= pct;
    }

    public double getPct() {
        return pct;
    }

    @Override
    public String toString() {
        return "mínimo de " + BigDecimal.valueOf(pct).stripTrailingZeros().toPlainString()
                + "% de presença";
    }
}
