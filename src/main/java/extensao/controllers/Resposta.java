package extensao.controllers;

import java.util.Map;

/**
 * Resposta de uma rota. O corpo é convertido em JSON, a não ser que seja
 * texto com um tipo definido (a página do cliente e o arquivo do certificado).
 */
record Resposta(int status, Object corpo, String local, String tipo) {

    static Resposta json(int status, Object corpo) {
        return new Resposta(status, corpo, null, null);
    }

    /** Escrita aceita (ver ADR 002). */
    static Resposta aceita(String mensagem) {
        return json(202, Map.of("mensagem", mensagem));
    }

    static Resposta texto(String tipo, String corpo) {
        return new Resposta(200, corpo, null, tipo);
    }

    static Resposta redirecionar(String local) {
        return new Resposta(302, null, local, null);
    }

    static Resposta erro(int status, String mensagem) {
        return json(status, Map.of("erro", String.valueOf(mensagem)));
    }
}
