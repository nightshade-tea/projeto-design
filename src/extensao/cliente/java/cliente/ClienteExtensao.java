package cliente;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * O cliente web só entrega as páginas ao navegador. As páginas conversam
 * direto com a API do servidor, cujo endereço vai em /config.js, e este
 * programa não conhece nada do servidor além desse endereço.
 */
public final class ClienteExtensao {

    private ClienteExtensao() {
    }

    /**
     * Uso: java -Dporta=8080 -Dapi=http://localhost:7080 -Dpaginas=pasta
     * cliente.ClienteExtensao
     */
    public static void main(String[] args) throws IOException {
        int porta = Integer.parseInt(System.getProperty("porta", "8080"));
        String api = System.getProperty("api", "http://localhost:7080");
        Path paginas = Path.of(System.getProperty("paginas", "src/extensao/cliente/resources"));

        HttpServer servidor = HttpServer.create(new InetSocketAddress(porta), 0);
        servidor.createContext("/", troca -> responder(troca, paginas, api));
        servidor.start();
        System.out.println("Cliente web: http://localhost:" + porta + "/, API em " + api);
    }

    private static void responder(HttpExchange troca, Path paginas, String api) throws IOException {
        String nome = troca.getRequestURI().getPath().substring(1);
        if (nome.isEmpty()) {
            nome = "index.html";
        }
        if (nome.equals("config.js")) {
            enviar(troca, 200, "text/javascript", "var API = '" + api + "';\n");
        } else if (nome.matches("[a-z]+\\.(html|js)") && Files.exists(paginas.resolve(nome))) {
            String tipo = nome.endsWith(".js") ? "text/javascript" : "text/html";
            enviar(troca, 200, tipo,
                    Files.readString(paginas.resolve(nome), StandardCharsets.UTF_8));
        } else {
            enviar(troca, 404, "text/plain", "página não encontrada");
        }
    }

    private static void enviar(HttpExchange troca, int status, String tipo, String corpo)
            throws IOException {
        byte[] bytes = corpo.getBytes(StandardCharsets.UTF_8);
        troca.getResponseHeaders().set("Content-Type", tipo + "; charset=utf-8");
        troca.sendResponseHeaders(status, bytes.length);
        try (OutputStream saida = troca.getResponseBody()) {
            saida.write(bytes);
        }
    }
}
