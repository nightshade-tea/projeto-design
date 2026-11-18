package extensao;

import extensao.dominio.certificacao.Certificado;
import extensao.dominio.certificacao.GeradorDocumentoCertificado;
import java.nio.charset.StandardCharsets;

/**
 * Gera um documento mínimo, só com os dados do certificado. Substitui o
 * gerador de produção nos testes sem mudar o domínio nem os services.
 */
public class GeradorDocumentoTeste implements GeradorDocumentoCertificado {

    @Override
    public byte[] gerar(Certificado certificado) {
        return (certificado.getId() + ";" + certificado.getNomeAluno() + ";"
                + certificado.getTituloProjeto() + ";" + certificado.getCargaHoraria())
                .getBytes(StandardCharsets.UTF_8);
    }
}
