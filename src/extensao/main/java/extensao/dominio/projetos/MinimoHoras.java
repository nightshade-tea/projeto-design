package extensao.dominio.projetos;

public class MinimoHoras implements CriterioCertificacao {

    private final int cargaHoraria;

    public MinimoHoras(int cargaHoraria) {
        if (cargaHoraria <= 0) {
            throw new IllegalArgumentException("o mínimo de horas deve ser positivo");
        }
        this.cargaHoraria = cargaHoraria;
    }

    @Override
    public boolean avaliar(ResumoFrequencia resumo) {
        return resumo.getHorasCumpridas() >= cargaHoraria;
    }

    public int getCargaHoraria() {
        return cargaHoraria;
    }
}
