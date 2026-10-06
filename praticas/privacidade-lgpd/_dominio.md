---
titulo: Privacidade e LGPD
grupo: Dados
descricao: "Dado pessoal tratado com classe, finalidade e máscara: do registro de classificação ao que não pode ir para prompt, log nem teste."
steering: [seguranca]
skills: [threat-model]
referencias: [lgpd]
candidatas:
  - titulo: Classifique o dado pessoal antes de escrever
    momento: antes-de-escrever
  - titulo: Dado pessoal não entra em prompt, log nem teste sem máscara
    momento: enquanto-escreve
  - titulo: RIPD antes do tratamento de alto risco
    momento: antes-de-escrever
revisado_em: 2026-10-06
---

Para a LGPD, dado pessoal é a informação relacionada a pessoa natural identificada ou
identificável, e o tratamento inclui da coleta ao armazenamento e à transmissão
[ref:lgpd]. A leitura do portal é que gravar, registrar e enviar a um modelo são tratamento, e as
práticas desta faixa levam essa leitura para o dia a dia do projeto: classificar o campo antes de
criá-lo e manter o dado pessoal fora de prompt, de log e de teste.
