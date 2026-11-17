package extensao.controllers;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import extensao.dominio.projetos.RegraNegocioException;
import extensao.services.NaoAutenticadoException;
import extensao.services.NaoEncontradoException;
import extensao.services.SemPermissaoException;
import java.io.IOException;
import java.io.OutputStream;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Encaminha cada requisição para a rota do controller e converte as exceções
 * nos códigos HTTP da API (ver arquitetura.md, seção API).
 * As páginas do cliente web vêm de outro endereço (origem), por isso as
 * respostas liberam essa origem a chamar a API com o cookie (CORS).
 */
public class Roteador implements HttpHandler {

    /** O que a rota faz; parametros são os grupos da expressão do caminho. */
    interface Acao {
        Resposta tratar(HttpExchange troca, List<String> parametros) throws IOException;
    }

    private record Rota(String metodo, Pattern caminho, Acao acao) {
    }

    private static final Logger LOG = Logger.getLogger(Roteador.class.getName());

    private final List<Rota> rotas = new ArrayList<>();
    private final String origemCliente;

    public Roteador(String origemCliente, Controller... controllers) {
        this.origemCliente = origemCliente;
        for (Controller c : controllers) {
            c.rotas(this);
        }
    }

    void rota(String metodo, String caminho, Acao acao) {
        rotas.add(new Rota(metodo, Pattern.compile(caminho), acao));
    }

    @Override
    public void handle(HttpExchange troca) throws IOException {
        troca.getResponseHeaders().set("Access-Control-Allow-Origin", origemCliente);
        troca.getResponseHeaders().set("Access-Control-Allow-Credentials", "true");
        if (troca.getRequestMethod().equals("OPTIONS")) {
            // o navegador pergunta antes de enviar JSON, PUT ou DELETE
            troca.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE");
            troca.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type, Authorization");
            troca.sendResponseHeaders(204, -1);
            troca.close();
            return;
        }
        Resposta resposta;
        try {
            resposta = encaminhar(troca);
        } catch (NaoAutenticadoException e) {
            resposta = Resposta.erro(401, e.getMessage());
        } catch (SemPermissaoException e) {
            resposta = Resposta.erro(403, e.getMessage());
        } catch (NaoEncontradoException e) {
            resposta = Resposta.erro(404, e.getMessage());
        } catch (RegraNegocioException e) {
            resposta = Resposta.erro(409, e.getMessage());
        } catch (IllegalArgumentException e) {
            resposta = Resposta.erro(400, e.getMessage());
        } catch (UncheckedIOException e) {
            resposta = Resposta.erro(503, e.getMessage());
        } catch (RuntimeException e) {
            LOG.log(Level.SEVERE, "erro ao tratar " + troca.getRequestURI(), e);
            resposta = Resposta.erro(500, "erro interno");
        }
        enviar(troca, resposta);
    }

    private Resposta encaminhar(HttpExchange troca) throws IOException {
        String caminho = troca.getRequestURI().getPath();
        boolean existe = false;
        for (Rota rota : rotas) {
            Matcher m = rota.caminho().matcher(caminho);
            if (!m.matches()) {
                continue;
            }
            existe = true;
            if (rota.metodo().equals(troca.getRequestMethod())) {
                List<String> parametros = new ArrayList<>();
                for (int i = 1; i <= m.groupCount(); i++) {
                    parametros.add(m.group(i));
                }
                return rota.acao().tratar(troca, parametros);
            }
        }
        return existe ? Resposta.erro(405, "método não permitido")
                : Resposta.erro(404, "rota não encontrada");
    }

    private static void enviar(HttpExchange troca, Resposta resposta) throws IOException {
        resposta.cabecalhos().forEach((nome, valor) -> troca.getResponseHeaders().set(nome, valor));
        if (resposta.corpo() == null) {
            troca.sendResponseHeaders(resposta.status(), -1);
            troca.close();
            return;
        }
        String tipo = resposta.tipo() == null ? "application/json" : resposta.tipo();
        String texto = resposta.tipo() == null ? Json.escrever(resposta.corpo())
                : resposta.corpo().toString();
        byte[] bytes = texto.getBytes(StandardCharsets.UTF_8);
        troca.getResponseHeaders().set("Content-Type", tipo + "; charset=utf-8");
        troca.sendResponseHeaders(resposta.status(), bytes.length);
        try (OutputStream saida = troca.getResponseBody()) {
            saida.write(bytes);
        }
    }
}
