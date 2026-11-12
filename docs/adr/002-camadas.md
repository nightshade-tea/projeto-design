# ADR 002: Uso de Camadas

## Status

Aceito

## Contexto

- O sistema depende de partes que podem mudar: o banco de dados, o login
  institucional e o formato do arquivo do certificado
- As regras de certificação devem poder mudar e crescer
- O domínio deve ser testável sem o banco e sem o provedor de identidade
- O domínio não deve depender de banco, HTTP ou serviços externos
- A equipe é pequena e o sistema é de porte médio

## Alternativas consideradas

- **Camadas**: controllers -> services -> dominio -> acesso a dados
- **Arquitetura Hexagonal ou Clean completa**: portas de entrada e saída,
  casos de uso e adaptadores separados para tudo

## Decisão

O código é organizado em **camadas**, e as dependências apontam para o
domínio:
- **Controllers** recebem requisições e identificam o usuário, sem regras de
  negócio
- **Services** executam os casos de uso
- **Domínio** tem os objetos e as regras
- **Interfaces** tem as interfaces mais generalizadas para tecnologias externas
  ou separadas
- **Implementações** dependem das interfaces para implementações mais concretas

As regras de certificação são implementações de `CriterioCertificacao`

## Consequências

### Positivas

- O domínio não depende do banco, do provedor nem do formato do arquivo
  (inversão de dependência)
- As implementações podem ser trocadas, e os testes usam implementações de
  teste (`ProvedorIdentidadeTeste`, `GeradorDocumentoTeste`)
- Novos critérios de certificação não alteram `Projeto` nem
  `CriteriosCertificacao`
- Menos camadas, conceitos e sobrecarga que uma arquitetura Hexagonal ou Clean
  completa

### Negativas, custos e riscos

- Os controllers e services não têm interfaces próprias, então trocar a
  forma de acesso exige mais mudanças do que na arquitetura Hexagonal
- Manter as dependências no sentido certo depende da disciplina da equipe
