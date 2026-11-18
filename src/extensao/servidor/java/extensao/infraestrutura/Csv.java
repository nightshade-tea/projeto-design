package extensao.infraestrutura;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;

/**
 * Leitura e escrita de arquivos CSV (RFC 4180): campos separados por
 * vírgula, entre aspas quando têm vírgula, aspas ou quebra de linha. A
 * primeira linha é o cabeçalho.
 */
final class Csv {

    private Csv() {
    }

    /** Linhas do arquivo, sem o cabeçalho, ou vazio se o arquivo não existir. */
    static List<List<String>> ler(Path arquivo) {
        if (!Files.exists(arquivo)) {
            return new ArrayList<>();
        }
        String texto;
        try {
            texto = Files.readString(arquivo, StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        List<List<String>> linhas = new ArrayList<>();
        List<String> linha = new ArrayList<>();
        StringBuilder campo = new StringBuilder();
        boolean aspas = false;
        boolean vazia = true;
        for (int i = 0; i < texto.length(); i++) {
            char c = texto.charAt(i);
            if (aspas) {
                if (c == '"' && i + 1 < texto.length() && texto.charAt(i + 1) == '"') {
                    campo.append('"');
                    i++;
                } else if (c == '"') {
                    aspas = false;
                } else {
                    campo.append(c);
                }
            } else if (c == '"') {
                aspas = true;
                vazia = false;
            } else if (c == ',') {
                linha.add(campo.toString());
                campo.setLength(0);
                vazia = false;
            } else if (c == '\n' || c == '\r') {
                if (c == '\r' && i + 1 < texto.length() && texto.charAt(i + 1) == '\n') {
                    i++;
                }
                if (!vazia || campo.length() > 0) {
                    linha.add(campo.toString());
                    linhas.add(linha);
                }
                linha = new ArrayList<>();
                campo.setLength(0);
                vazia = true;
            } else {
                campo.append(c);
                vazia = false;
            }
        }
        if (!vazia || campo.length() > 0) {
            linha.add(campo.toString());
            linhas.add(linha);
        }
        return linhas.isEmpty() ? linhas : new ArrayList<>(linhas.subList(1, linhas.size()));
    }

    /** Reescreve o arquivo inteiro de uma vez (grava em um temporário e troca). */
    static void escrever(Path arquivo, List<String> cabecalho, List<List<String>> linhas) {
        StringBuilder texto = new StringBuilder();
        linha(texto, cabecalho);
        linhas.forEach(l -> linha(texto, l));
        try {
            Path pasta = arquivo.toAbsolutePath().getParent();
            Files.createDirectories(pasta);
            Path temporario = Files.createTempFile(pasta, arquivo.getFileName().toString(), ".tmp");
            Files.writeString(temporario, texto, StandardCharsets.UTF_8);
            Files.move(temporario, arquivo, StandardCopyOption.REPLACE_EXISTING,
                    StandardCopyOption.ATOMIC_MOVE);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private static void linha(StringBuilder texto, List<String> campos) {
        for (int i = 0; i < campos.size(); i++) {
            if (i > 0) {
                texto.append(',');
            }
            String c = campos.get(i) == null ? "" : campos.get(i);
            if (c.contains(",") || c.contains("\"") || c.contains("\n") || c.contains("\r")) {
                texto.append('"').append(c.replace("\"", "\"\"")).append('"');
            } else {
                texto.append(c);
            }
        }
        texto.append('\n');
    }
}
