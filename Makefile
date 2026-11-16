# Protótipo (src/): só precisa do JDK 21 ou mais novo
#   make run      login institucional simulado (:8081) e servidor com o cliente web (:8080)
#   make login / make servidor   cada um separado
#   make test     testes
#   make cenario  reproduz o diagrama de sequência completo por HTTP
#
# Dois programas separados, cada um com o seu código:
#   src/extensao       servidor do sistema (com o cliente web)
#   src/institucional  login institucional simulado

BUILD       := build
DADOS       := dados
PORTA       := 8080
PORTA_LOGIN := 8081
USUARIOS    := src/institucional/main/resources/usuarios.csv
CLIENTE     := src/extensao/main/resources/cliente
JAVAC       := javac --release 21 -encoding UTF-8

EXTENSAO      := $(shell find src/extensao/main/java -name '*.java')
INSTITUCIONAL := $(shell find src/institucional/main/java -name '*.java')
TESTES        := $(shell find src/extensao/test/java -name '*.java')

# os testes sobem os dois programas
CP_TESTES := $(BUILD)/extensao:$(BUILD)/institucional:$(BUILD)/testes

.PHONY: build run login servidor test cenario clean

build: $(BUILD)/.extensao $(BUILD)/.institucional

$(BUILD)/.extensao: $(EXTENSAO)
	rm -rf $(BUILD)/extensao
	$(JAVAC) -d $(BUILD)/extensao $(EXTENSAO)
	touch $@

$(BUILD)/.institucional: $(INSTITUCIONAL)
	rm -rf $(BUILD)/institucional
	$(JAVAC) -d $(BUILD)/institucional $(INSTITUCIONAL)
	touch $@

$(BUILD)/.testes: build $(TESTES)
	rm -rf $(BUILD)/testes
	$(JAVAC) -cp $(BUILD)/extensao:$(BUILD)/institucional -d $(BUILD)/testes $(TESTES)
	touch $@

# Ctrl+C para os dois
run: build
	trap 'kill 0' EXIT; \
	java -Dporta=$(PORTA_LOGIN) -Dusuarios=$(USUARIOS) -cp $(BUILD)/institucional institucional.LoginInstitucional & \
	java -Dporta=$(PORTA) -DurlLogin=http://localhost:$(PORTA_LOGIN) -Ddados=$(DADOS) \
		-Dcliente=$(CLIENTE) -cp $(BUILD)/extensao extensao.Main & \
	wait

login: $(BUILD)/.institucional
	java -Dporta=$(PORTA_LOGIN) -Dusuarios=$(USUARIOS) -cp $(BUILD)/institucional institucional.LoginInstitucional

servidor: $(BUILD)/.extensao
	java -Dporta=$(PORTA) -DurlLogin=http://localhost:$(PORTA_LOGIN) -Ddados=$(DADOS) \
		-Dcliente=$(CLIENTE) -cp $(BUILD)/extensao extensao.Main

test: $(BUILD)/.testes
	java -cp $(CP_TESTES) extensao.Testes

cenario: $(BUILD)/.testes
	java -cp $(CP_TESTES) extensao.Cenario

clean:
	rm -rf $(BUILD)
