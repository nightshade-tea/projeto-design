package extensao.infraestrutura;

import extensao.dominio.certificacao.Certificado;
import extensao.dominio.certificacao.GeradorDocumentoCertificado;
import java.nio.charset.StandardCharsets;
import java.time.format.DateTimeFormatter;

/**
 * Gera o certificado como um arquivo de texto, no lugar do GeradorPdf de
 * arquitetura.md. Trocar o formato muda só esta classe.
 */
public class GeradorTxt implements GeradorDocumentoCertificado {

    private static final DateTimeFormatter DATA = DateTimeFormatter.ofPattern("dd/MM/yyyy");

    @Override
    public byte[] gerar(Certificado certificado) {
        String texto = """
                CERTIFICADO DE PARTICIPAÇÃO EM PROJETO DE EXTENSÃO

                Certificamos que %s participou do projeto de extensão
                "%s", coordenado por %s, com carga horária de %d horas.

                Emitido em %s.
                Certificado número %d
                """.formatted(certificado.getNomeAluno(), certificado.getTituloProjeto(),
                certificado.getNomeCoordenador(), certificado.getCargaHoraria(),
                certificado.getEmitidoEm().format(DATA), certificado.getId());
        return texto.getBytes(StandardCharsets.UTF_8);
    }
}
