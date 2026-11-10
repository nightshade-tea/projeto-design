package extensao.dominio.certificacao;

/** Isola o formato do arquivo do certificado. */
public interface GeradorDocumentoCertificado {

    /** Produz o arquivo que o aluno baixa. */
    byte[] gerar(Certificado certificado);
}
