package extensao.controllers;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * JSON mínimo para o protótipo não depender de bibliotecas: lê objetos
 * planos com valores texto e escreve mapas, listas, textos e números.
 */
final class Json {

    private Json() {
    }

    static Map<String, String> lerObjeto(String texto) {
        Leitor l = new Leitor(texto);
        Map<String, String> objeto = new LinkedHashMap<>();
        l.esperar('{');
        if (!l.consumir('}')) {
            do {
                String chave = l.texto();
                l.esperar(':');
                objeto.put(chave, l.texto());
            } while (l.consumir(','));
            l.esperar('}');
        }
        l.fim();
        return objeto;
    }

    static String escrever(Object valor) {
        StringBuilder s = new StringBuilder();
        escrever(s, valor);
        return s.toString();
    }

    private static void escrever(StringBuilder s, Object valor) {
        if (valor == null) {
            s.append("null");
        } else if (valor instanceof Number || valor instanceof Boolean) {
            s.append(valor);
        } else if (valor instanceof Map<?, ?> mapa) {
            s.append('{');
            boolean primeiro = true;
            for (Map.Entry<?, ?> e : mapa.entrySet()) {
                if (!primeiro) {
                    s.append(',');
                }
                primeiro = false;
                escrever(s, String.valueOf(e.getKey()));
                s.append(':');
                escrever(s, e.getValue());
            }
            s.append('}');
        } else if (valor instanceof List<?> lista) {
            s.append('[');
            for (int i = 0; i < lista.size(); i++) {
                if (i > 0) {
                    s.append(',');
                }
                escrever(s, lista.get(i));
            }
            s.append(']');
        } else {
            s.append('"');
            for (char c : valor.toString().toCharArray()) {
                switch (c) {
                    case '"' -> s.append("\\\"");
                    case '\\' -> s.append("\\\\");
                    case '\n' -> s.append("\\n");
                    case '\r' -> s.append("\\r");
                    case '\t' -> s.append("\\t");
                    default -> {
                        if (c < 0x20) {
                            s.append(String.format("\\u%04x", (int) c));
                        } else {
                            s.append(c);
                        }
                    }
                }
            }
            s.append('"');
        }
    }

    private static final class Leitor {

        private final String s;
        private int i;

        Leitor(String s) {
            this.s = s == null ? "" : s;
        }

        void pular() {
            while (i < s.length() && Character.isWhitespace(s.charAt(i))) {
                i++;
            }
        }

        boolean consumir(char c) {
            pular();
            if (i < s.length() && s.charAt(i) == c) {
                i++;
                return true;
            }
            return false;
        }

        void esperar(char c) {
            if (!consumir(c)) {
                throw new IllegalArgumentException("JSON inválido: esperava '" + c + "'");
            }
        }

        void fim() {
            pular();
            if (i != s.length()) {
                throw new IllegalArgumentException("JSON inválido: texto depois do objeto");
            }
        }

        String texto() {
            esperar('"');
            StringBuilder r = new StringBuilder();
            while (i < s.length()) {
                char c = s.charAt(i++);
                if (c == '"') {
                    return r.toString();
                }
                if (c != '\\') {
                    r.append(c);
                    continue;
                }
                if (i >= s.length()) {
                    break;
                }
                char e = s.charAt(i++);
                switch (e) {
                    case 'n' -> r.append('\n');
                    case 't' -> r.append('\t');
                    case 'r' -> r.append('\r');
                    case 'b' -> r.append('\b');
                    case 'f' -> r.append('\f');
                    case 'u' -> {
                        if (i + 4 > s.length()) {
                            throw new IllegalArgumentException(
                                    "JSON inválido: escape \\u incompleto");
                        }
                        r.append((char) Integer.parseInt(s.substring(i, i + 4), 16));
                        i += 4;
                    }
                    default -> r.append(e);
                }
            }
            throw new IllegalArgumentException("JSON inválido: texto sem fim");
        }
    }
}
