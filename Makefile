# Protótipo (src/): só precisa do JDK 21 ou mais novo
#   make run      login institucional simulado (:8081) e servidor com o cliente web (:8080)
#   make login / make servidor   cada um separado
#   make test     testes
#   make cenario  reproduz o diagrama de sequência completo por HTTP

OUT        := src/out
DADOS      := src/dados
PORTA      := 8080
PORTA_LOGIN := 8081
USUARIOS   := src/main/resources/usuarios-institucionais.csv
CLIENTE    := src/main/resources/cliente.html
JAVAC      := javac --release 21 -encoding UTF-8

MAIN := $(shell find src/main/java -name '*.java')
TEST := $(shell find src/test/java -name '*.java')

.PHONY: build run login servidor test cenario clean

build: $(OUT)/.main

$(OUT)/.main: $(MAIN)
	rm -rf $(OUT)/main
	$(JAVAC) -d $(OUT)/main $(MAIN)
	touch $@

$(OUT)/.test: $(OUT)/.main $(TEST)
	rm -rf $(OUT)/test
	$(JAVAC) -cp $(OUT)/main -d $(OUT)/test $(TEST)
	touch $@

# login institucional e servidor são programas separados; run sobe os dois
# (Ctrl+C para os dois)
run: build
	trap 'kill 0' EXIT; \
	java -Dporta=$(PORTA_LOGIN) -Dusuarios=$(USUARIOS) -cp $(OUT)/main institucional.LoginInstitucional & \
	java -Dporta=$(PORTA) -DurlLogin=http://localhost:$(PORTA_LOGIN) -Ddados=$(DADOS) \
		-Dcliente=$(CLIENTE) -cp $(OUT)/main extensao.Main & \
	wait

login: build
	java -Dporta=$(PORTA_LOGIN) -Dusuarios=$(USUARIOS) -cp $(OUT)/main institucional.LoginInstitucional

servidor: build
	java -Dporta=$(PORTA) -DurlLogin=http://localhost:$(PORTA_LOGIN) -Ddados=$(DADOS) \
		-Dcliente=$(CLIENTE) -cp $(OUT)/main extensao.Main

test: $(OUT)/.test
	java -cp $(OUT)/main:$(OUT)/test extensao.Testes

cenario: $(OUT)/.test
	java -cp $(OUT)/main:$(OUT)/test extensao.Cenario

clean:
	rm -rf $(OUT)
