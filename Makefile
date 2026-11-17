# protótipo jdk >= 21
# make run | cliente | servidor | login | test | cenario | clean

BUILD := build
DADOS := dados

PORTA_CLIENTE  := 8080
PORTA_SERVIDOR := 7080
PORTA_LOGIN    := 9080
URL_CLIENTE    := http://localhost:$(PORTA_CLIENTE)
URL_SERVIDOR   := http://localhost:$(PORTA_SERVIDOR)
URL_LOGIN      := http://localhost:$(PORTA_LOGIN)

PAGINAS  := src/extensao/cliente/resources
USUARIOS := src/institucional/resources/usuarios.csv

JAVAC := javac --release 21 -encoding UTF-8

CLIENTE       := $(shell find src/extensao/cliente/java -name '*.java')
SERVIDOR      := $(shell find src/extensao/servidor/java -name '*.java')
INSTITUCIONAL := $(shell find src/institucional/java -name '*.java')
TESTES        := $(shell find src/extensao/servidor/test -name '*.java')

# os testes sobem o servidor e o login institucional
CP_TESTES := $(BUILD)/servidor:$(BUILD)/institucional:$(BUILD)/testes

RODAR_CLIENTE  = java -Dporta=$(PORTA_CLIENTE) -Dapi=$(URL_SERVIDOR) -Dpaginas=$(PAGINAS) \
	-cp $(BUILD)/cliente cliente.ClienteExtensao
RODAR_SERVIDOR = java -Dporta=$(PORTA_SERVIDOR) -DurlLogin=$(URL_LOGIN) -DurlCliente=$(URL_CLIENTE) \
	-Ddados=$(DADOS) -cp $(BUILD)/servidor extensao.ServidorExtensao
RODAR_LOGIN    = java -Dporta=$(PORTA_LOGIN) -Dusuarios=$(USUARIOS) \
	-cp $(BUILD)/institucional institucional.LoginInstitucional

.PHONY: build run cliente servidor login test cenario clean

build: $(BUILD)/.cliente $(BUILD)/.servidor $(BUILD)/.institucional

$(BUILD)/.cliente: $(CLIENTE)
	rm -rf $(BUILD)/cliente
	$(JAVAC) -d $(BUILD)/cliente $(CLIENTE)
	touch $@

$(BUILD)/.servidor: $(SERVIDOR)
	rm -rf $(BUILD)/servidor
	$(JAVAC) -d $(BUILD)/servidor $(SERVIDOR)
	touch $@

$(BUILD)/.institucional: $(INSTITUCIONAL)
	rm -rf $(BUILD)/institucional
	$(JAVAC) -d $(BUILD)/institucional $(INSTITUCIONAL)
	touch $@

$(BUILD)/.testes: $(BUILD)/.servidor $(BUILD)/.institucional $(TESTES)
	rm -rf $(BUILD)/testes
	$(JAVAC) -cp $(BUILD)/servidor:$(BUILD)/institucional -d $(BUILD)/testes $(TESTES)
	touch $@

run: build
	trap 'kill 0' EXIT; \
	$(RODAR_LOGIN) & $(RODAR_SERVIDOR) & $(RODAR_CLIENTE) & \
	wait

cliente: $(BUILD)/.cliente
	$(RODAR_CLIENTE)

servidor: $(BUILD)/.servidor
	$(RODAR_SERVIDOR)

login: $(BUILD)/.institucional
	$(RODAR_LOGIN)

test: $(BUILD)/.testes
	java -cp $(CP_TESTES) extensao.Testes

cenario: $(BUILD)/.testes
	java -cp $(CP_TESTES) extensao.Cenario

clean:
	rm -rf $(BUILD)
