---
id: SEG-04
titulo: Configuração insegura aborta o boot em produção
marco: "boot falha fechado"
dominio: seguranca
subdominio: null
momento: enquanto-escreve
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [owasp-top10-2025-a02, twelve-factor-config, pydantic-settings, pydantic-config, django-deployment-checklist, spring-boot-external-config]
relacionadas: [SEG-02, SEG-05]
dono: engenharia
revisado_em: 2026-11-03
revisar_ate: 2027-05-03
resumo: "A aplicação lê a configuração do ambiente, confere no boot e, em produção, se recusa a subir com debug ligado, chave fraca ou CORS aberto."
ferramentas_aprovadas: []
exemplos:
  - exemplos/SEG-04/config.py
---

## O que fazer

A configuração é conferida uma vez, no boot, antes de a aplicação aceitar a primeira requisição. Em
produção, um valor inseguro não vira aviso no log: o processo sai com erro e não sobe. A OWASP lista
entre as falhas de configuração as contas padrão ainda ativas, o recurso desnecessário habilitado, a
mensagem de erro que mostra stack trace e a configuração de segurança do framework que não está num
valor seguro, e recomenda um processo automatizado que verifique a configuração em todos os ambientes
[ref:owasp-top10-2025-a02]. A conferência no boot é esse processo no ponto em que ele não pode ser
pulado.

1. **A configuração vem do ambiente.** Configuração é o que varia entre deploys, e fica em variável de
   ambiente, separada do código [ref:twelve-factor-config]. O segredo segue a SEG-02.
2. **Sem padrão inseguro.** Campo que só tem valor seguro em produção não tem valor padrão no código: a
   chave de sessão e o nome do ambiente são obrigatórios, e a ausência derruba o boot. O padrão que
   existe é o seguro (`debug` desligado, documentação interna fechada, CORS vazio).
3. **Regra por ambiente, em código.** Com `ambiente=producao`, o boot recusa `debug` ligado, chave curta,
   CORS que aceita qualquer origem e documentação interna pública. A lista é do projeto; o Exemplo traz
   quatro itens.
4. **O erro diz o quê, nunca o valor.** A mensagem nomeia a variável e o problema, e não repete o que
   foi lido: o valor pode ser a chave.

## Como aparece quando falta

O `config.py` lê `APP_DEBUG` com padrão `true` e a chave de sessão com padrão `"dev"`, para o projeto
rodar sem preparo na máquina de quem desenvolve. No deploy, alguém esquece uma variável, e a aplicação
sobe em produção com o modo de depuração e a chave conhecida por todo mundo que leu o repositório. Nada
falha: o problema aparece quando uma página de erro mostra o stack trace a um usuário, que a OWASP cita
como uma das formas da falha [ref:owasp-top10-2025-a02], ou quando alguém forja uma sessão com a chave
padrão. O Django diz o mesmo da depuração: nunca a ligue em produção [ref:django-deployment-checklist].

## Como aplicar

1. Junte a configuração num só módulo, lido uma vez no boot. Nenhum outro arquivo lê `os.environ`.
2. Declare cada campo com tipo. Tire o padrão de todo campo que só tem valor seguro em produção. No
   pydantic-settings, cada campo de uma classe `BaseSettings` é lido da variável de ambiente de mesmo
   nome, sem distinção de maiúsculas por padrão e com o prefixo de `env_prefix`, e o campo obrigatório
   ausente vira erro de validação [ref:pydantic-settings].
3. Escreva a regra de produção como validação do próprio objeto de configuração (no Exemplo, um
   `model_validator`), e não como `if` espalhado pela aplicação.
4. Faça a falha não repetir o valor. No pydantic, `hide_input_in_errors` esconde o valor recebido na
   mensagem de erro; o padrão é mostrá-lo [ref:pydantic-config]. Na execução do portal, sem essa opção,
   o erro do validador repetiu a chave lida do ambiente.
5. No ponto de entrada, capture o erro, escreva uma linha por problema em stderr e saia com 1, antes de
   abrir a porta. O orquestrador vê o processo falhar e não põe a versão nova no ar.
6. Escreva um teste por regra: com `ambiente=producao` e o valor inseguro, o carregamento falha; com o
   valor seguro, passa.

## Exemplo

### Antes e depois

Antes, cada variável tem um padrão que só serve para a máquina de quem desenvolve:

```python
import os

DEBUG = os.environ.get("APP_DEBUG", "true") == "true"
CHAVE_DE_SESSAO = os.environ.get("APP_CHAVE_DE_SESSAO", "dev")
ORIGENS_CORS = os.environ.get("APP_ORIGENS_CORS", "*").split(",")
```

Depois, com o pydantic-settings, a configuração é um objeto validado no boot (o arquivo completo está
em `exemplos/SEG-04/config.py`):

<!-- incluir: exemplos/SEG-04/config.py -->

Executado com `uv run --no-project --with pydantic-settings==2.16.2 python config.py` (pydantic
2.14.2), em produção com debug ligado, chave curta e CORS aberto, o processo sai com 1:

```text
boot abortado: config: Value error, configuração insegura em produção: APP_DEBUG ligado; APP_CHAVE_DE_SESSAO com menos de 32 caracteres; APP_ORIGENS_CORS aceita qualquer origem
```

Sem `APP_CHAVE_DE_SESSAO`, também sai com 1 (`boot abortado: chave_de_sessao: Field required`). Com
uma chave de 40 caracteres e uma origem explícita, sai com 0 (`configuração ok para producao`); com
`APP_AMBIENTE=local`, debug ligado e chave curta passam, porque a regra é de produção.

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Configuração só no módulo de configuração, lida do ambiente e validada no boot. Campo que só é seguro
em produção não tem valor padrão. Em produção, debug ligado, chave curta, CORS com * e documentação
interna pública abortam o boot. A mensagem de erro nomeia a variável e nunca mostra o valor.
```

Prompt para trocar um módulo de configuração com padrões inseguros:

```prompt
Aplique a prática SEG-04 do portal de padrões de engenharia neste repositório.

1. Leia app/config.py, que hoje lê APP_DEBUG, APP_CHAVE_DE_SESSAO e APP_ORIGENS_CORS de os.environ
   com valores padrão. Reescreva-o com pydantic-settings: uma classe Config(BaseSettings) com
   env_prefix "APP_" e hide_input_in_errors=True; os campos ambiente (local, homologacao ou
   producao, sem padrão), debug (padrão False), chave_de_sessao (SecretStr, sem padrão) e
   origens_cors (lista, padrão vazia).
2. Acrescente um model_validator que, só com ambiente producao, recusa debug ligado, chave com menos
   de 32 caracteres e "*" em origens_cors, com uma mensagem que nomeia a variável e nunca o valor.
3. Crie a função carregar(), que devolve a Config ou escreve uma linha por erro em stderr e sai com 1.
   Não mude outro arquivo.
4. Escreva tests/test_config.py com três casos: produção com debug ligado sai com 1; produção sem a
   chave sai com 1; produção com chave de 40 caracteres e origem explícita carrega. Rode os testes e
   mostre a saída. Confirme que nenhuma saída de erro contém o valor da chave usado no teste.
```

Antes de rodar, o repositório precisa ter o `app/config.py` do "Antes", o `pytest` e o
`pydantic-settings` instalados.

### Por ferramenta

- **Django:** `manage.py check --deploy` confere parte dessas regras e deve rodar contra o settings de
  produção; a chave sai do ambiente, com `SECRET_KEY = os.environ["SECRET_KEY"]`
  [ref:django-deployment-checklist]. Rode o comando no CI, com o settings de produção, além da
  validação no boot.
- **Spring Boot:** a classe `@ConfigurationProperties` anotada com `@Validated` é validada, com as
  anotações de restrição do `jakarta.validation` nos campos [ref:spring-boot-external-config]. A regra
  que depende do perfil (produção) fica num validador da própria classe.

## Como verificar

Não há mecanismo: a força é `orienta`. A verificação é o teste do passo 6 do Como aplicar, que roda na
suíte do CI, e a revisão da MR que toca o módulo de configuração. Um verificador candidato acusaria, no
diff, `os.environ.get` com padrão em arquivo fora do módulo de configuração; ele não existe no portal,
porque a regra de produção é do projeto e não se lê do código com segurança.

Os limites: a conferência vê só o que está na lista do projeto, e um valor inseguro que ninguém pôs na
lista passa. Ela roda no boot, e não protege uma configuração que muda depois, em tempo de execução. O
`ambiente` errado (produção declarada como `homologacao`) desliga a regra: o valor de `APP_AMBIENTE`
vem do pipeline de deploy, e não de quem roda o processo à mão.
