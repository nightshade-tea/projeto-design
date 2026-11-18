package extensao.controllers;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Resposta de uma rota. O corpo é convertido em JSON, a não ser que seja
 * texto com um tipo definido (as páginas do cliente e o arquivo do certificado).
 */
record Resposta(int status, Object corpo, String tipo, Map<String, String> cabecalhos) {

    static Resposta json(int status, Object corpo) {
        return new Resposta(status, corpo, null, new LinkedHashMap<>());
    }

    /** Escrita aceita (ver arquitetura.md, Comunicação). */
    static Resposta aceita(String mensagem) {
        return json(202, Map.of("mensagem", mensagem));
    }

    static Resposta texto(String tipo, String corpo) {
        return new Resposta(200, corpo, tipo, new LinkedHashMap<>());
    }

    static Resposta redirecionar(String local) {
        return new Resposta(302, null, null, new LinkedHashMap<>()).com("Location", local);
    }

    static Resposta erro(int status, String mensagem) {
        return json(status, Map.of("erro", String.valueOf(mensagem)));
    }

    Resposta com(String cabecalho, String valor) {
        cabecalhos.put(cabecalho, valor);
        return this;
    }
}
