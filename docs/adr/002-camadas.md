# ADR 002: Uso de camadas

## Contexto

- O sistema é um monólito modular, de porte médio, mantido por uma equipe
  pequena
- O sistema depende de partes que podem mudar: o banco de dados, o login
  institucional e o formato do arquivo do certificado
- As regras de certificação devem poder mudar e crescer

## Problemas envolvidos

É preciso decidir como organizar o código dentro da aplicação:
- o domínio não deve depender de banco, HTTP ou serviços externos
- o domínio deve ser testável sem o banco e sem o provedor de identidade
- trocar o banco, o provedor ou o formato do arquivo não deve afetar as
  regras de negócio
- a organização não deve trazer mais conceitos e código do que a equipe
  consegue manter

## Alternativas consideradas

- **Camadas tradicionais**: controllers -> services -> domínio -> acesso a
  dados, com o domínio dependendo do acesso a dados
- **Camadas com inversão de dependência**: as interfaces de acesso a dados e
  a serviços externos ficam no domínio, e as implementações dependem delas
- **Arquitetura Hexagonal ou Clean completa**: portas de entrada e saída,
  casos de uso e adaptadores separados para tudo

## Decisão

O código é organizado em **camadas com inversão de dependência**, e as
dependências apontam para o domínio:
- **Controllers** recebem requisições e identificam o usuário, sem regras de
  negócio
- **Services** executam os casos de uso
- **Domínio** tem os objetos e as regras
- **Interfaces** têm as interfaces, definidas nos módulos do domínio, para o
  banco de dados, o provedor de identidade e a geração do arquivo
- **Infraestrutura** tem as implementações concretas dessas interfaces, e
  depende delas

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
- Mais interfaces e classes para manter do que nas camadas tradicionais
- Nada impede que um controller ou service use a infraestrutura
  diretamente, o que depende da disciplina da equipe
