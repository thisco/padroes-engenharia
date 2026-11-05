---
id: SEG-06
titulo: "Varredura de imagem e SAST como gate, ao lado da varredura de segredo"
marco: "imagem e código varridos na MR"
dominio: seguranca
subdominio: null
momento: antes-do-merge
forca: avisa
mecanismo:
  verificador: verificadores/seg_06.py
  gatilhos:
    - evento: antes-de-ferramenta
      ferramenta: [editar, escrever]
    - evento: ci
  mensagem: "SEG-06: o repositório constrói imagem ou tem código e o CI não tem job de varredura de imagem (trivy, grype, container_scanning) ou de SAST (semgrep, codeql, sast); acrescente o job que falha com achado. Como aplicar: {URL do portal}/praticas/SEG-06.md#como-aplicar"
status: experimentar
aplica: []
referencias: [owasp-top10-2025-a03, trivy-imagem-de-container, trivy-exit-code, trivy-action, semgrep-cli, gitlab-container-scanning, gitlab-container-scanning-template, gitlab-sast, gitlab-sast-template, gitlab-allow-failure, gitlab-politicas-de-aprovacao, gitlab-mr-pipelines, gitlab-pipeline-obrigatorio, github-branch-protegida, github-codeql, grype-limite-de-falha, github-actions-uso-seguro, docker-pull-por-digest, gitlab-registro-build-e-push, gitlab-docker-build, gitlab-variaveis-predefinidas, gitlab-include-local, gitlab-pipelines-downstream]
relacionadas: [SEG-02, SEG-03, CICD-01]
dono: engenharia
revisado_em: 2026-11-04
revisar_ate: 2027-05-04
resumo: "A MR passa por dois jobs que falham com achado: um varre a imagem construída, outro o código; o verificador do portal avisa quando o CI não tem um deles."
ferramentas_aprovadas: []
exemplos:
  - exemplos/SEG-06/antes/Dockerfile
  - exemplos/SEG-06/antes/app.py
  - exemplos/SEG-06/depois/Dockerfile
  - exemplos/SEG-06/depois/app.py
  - exemplos/SEG-06/gitlab-ci.yml
  - exemplos/SEG-06/github-workflow.yml
---

## O que fazer

A SEG-02 barra o segredo na MR. Esta prática põe, no mesmo pipeline, mais dois jobs que reprovam a
MR: um varre a imagem de contêiner que o projeto constrói, outro varre o código-fonte (SAST). A OWASP
põe entre as falhas de cadeia de suprimento não varrer vulnerabilidades com regularidade e rodar
software vulnerável, sem suporte ou desatualizado, inclusive o sistema operacional
[ref:owasp-top10-2025-a03]. A prática tem quatro partes.

1. **Varredura da imagem.** O Trivy varre os arquivos dentro da imagem atrás de vulnerabilidade,
   misconfiguração, segredo e licença, com vulnerabilidade e segredo ligados por padrão
   [ref:trivy-imagem-de-container]. Por padrão ele sai com 0 mesmo quando acha problema; o
   `--exit-code 1`, com `--severity`, faz o job falhar só a partir da severidade escolhida
   [ref:trivy-exit-code]. O Grype é a alternativa: com `--fail-on`, sai com 2 quando acha
   vulnerabilidade na severidade dada ou acima [ref:grype-limite-de-falha].
2. **SAST do código.** O Semgrep sai com 0 quando acha problema, a menos que rode com `--error`, que
   faz achado virar saída 1 [ref:semgrep-cli]. O `--metrics off` desliga o envio de métricas de uso
   ao servidor do Semgrep [ref:semgrep-cli].
3. **O job falha, não avisa.** Os templates do GitLab ligam a varredura, mas não reprovam: o job
   `container_scanning` do template de Container Scanning e os analisadores do template de SAST vêm
   com `allow_failure: true` [ref:gitlab-container-scanning-template] [ref:gitlab-sast-template], e
   o job com `allow_failure: true` que falha deixa só um aviso laranja, com o pipeline bem-sucedido
   [ref:gitlab-allow-failure]. Para reprovar a MR pelo achado, ou o job roda o scanner com o código
   de saída ligado (o Exemplo), ou o projeto usa a política de aprovação de MR do GitLab, que é do
   tier Ultimate e exige aprovação a partir do resultado dos scanners
   [ref:gitlab-politicas-de-aprovacao].
4. **O pipeline é obrigatório.** No GitLab, o merge check **Pipelines must succeed** exige um
   pipeline completo e bem-sucedido antes do merge [ref:gitlab-pipeline-obrigatorio]; no GitHub, a
   proteção de branch com **Require status checks before merging** exige que os checks marcados
   estejam com status `successful`, `skipped` ou `neutral` [ref:github-branch-protegida].

## Como aparece quando falta

O projeto tem o job de segredo da SEG-02 e mais nada. O `Dockerfile` parte de uma imagem base de
anos atrás, e ninguém olha os pacotes do sistema que vêm com ela; o código monta um comando de shell
com o nome de arquivo que o usuário mandou. As duas coisas passam na revisão, porque o diff é uma
linha do `FROM` e uma chamada a `subprocess`. É o quadro da OWASP: componente vulnerável e
desatualizado, inclusive o sistema operacional, sem varredura regular [ref:owasp-top10-2025-a03]. Ou o
projeto incluiu os templates de segurança do GitLab e acha que está protegido, mas o job com achado
fica laranja e a MR entra [ref:gitlab-allow-failure].

## Como aplicar

1. Acrescente ao CI os jobs do Exemplo (`gitlab-ci.yml` ou `github-workflow.yml`), sem
   `allow_failure`. No GitLab, os dois jobs de varredura ficam no stage `travas`, o mesmo do job de
   segredo da SEG-02, e rodam na MR com a regra `$CI_PIPELINE_SOURCE == "merge_request_event"`
   [ref:gitlab-mr-pipelines]. Fixe o que o CI baixa pelo identificador que não muda: a action do
   GitHub pelo SHA do commit, com a tag num comentário, porque a tag pode ser movida ou apagada por
   quem ganhar acesso ao repositório da action [ref:github-actions-uso-seguro]; a imagem do scanner
   pela tag e pelo digest, que fixa a versão exata [ref:docker-pull-por-digest]. Em troca, nada se
   atualiza sozinho, nem com correção de segurança [ref:docker-pull-por-digest]: suba a versão numa MR
   própria, trocando o SHA ou o digest junto com a tag. O Exemplo diz de onde veio cada um (`git
   ls-remote` no repositório da action, `docker buildx imagetools inspect` na imagem).
2. A varredura de imagem precisa da imagem construída. No GitLab, o job `construir-imagem` do Exemplo
   constrói e publica a imagem no registro do projeto, com `docker login` por `CI_REGISTRY_USER` e
   `CI_REGISTRY_PASSWORD`, `docker build` e `docker push` num serviço Docker-in-Docker
   [ref:gitlab-registro-build-e-push]; o Docker-in-Docker exige o runner em modo `privileged`, e sem
   ele o projeto usa uma alternativa ao Docker [ref:gitlab-docker-build]. A tag é
   `$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA`, com a revisão para a qual o pipeline roda
   [ref:gitlab-variaveis-predefinidas]: o build e a varredura leem a mesma variável no mesmo
   pipeline e apontam para a mesma imagem, e o `needs` faz a varredura esperar o build. Se o projeto
   já tem um job de build, aponte a varredura para a tag que ele publica, com a mesma regra de MR. O
   Trivy lê a imagem do registro (ele procura no Docker Engine local, depois no containerd, no Podman
   e no registro) [ref:trivy-imagem-de-container]. No GitHub Actions, o workflow constrói a imagem e
   a `trivy-action` a varre com `image-ref`, `exit-code: "1"` e `severity` [ref:trivy-action].
3. Comece a severidade por `HIGH,CRITICAL` [ref:trivy-exit-code]. Se o primeiro pipeline reprovar
   por pacote da imagem base, troque a base ou tire o pacote que não roda em produção, antes de
   pensar em ignorar o achado. O Exemplo faz as duas coisas.
4. Quem prefere o que o GitLab mantém usa os templates: `Jobs/Container-Scanning.gitlab-ci.yml`,
   com a imagem em `CS_IMAGE`, que usa o Trivy [ref:gitlab-container-scanning], e
   `Jobs/SAST.gitlab-ci.yml`, cujo analisador padrão é baseado no Semgrep, no job `semgrep-sast`, e
   que exige o stage `test` [ref:gitlab-sast]. Nos dois, o relatório JSON sai como artefato do job
   no Free [ref:gitlab-container-scanning] [ref:gitlab-sast]; o resultado de Container Scanning na MR
   é do Ultimate [ref:gitlab-container-scanning], e a gestão de vulnerabilidades do SAST também
   [ref:gitlab-sast].
   Como os jobs vêm com `allow_failure: true` [ref:gitlab-container-scanning-template]
   [ref:gitlab-sast-template], o achado só reprova a MR com a política de aprovação do Ultimate
   [ref:gitlab-politicas-de-aprovacao]; sem ela, prefira os jobs do Exemplo. No GitHub, o CodeQL é a
   opção nativa de SAST, ligada pelo default setup ou por um workflow com a `github/codeql-action`
   [ref:github-codeql].
5. Marque o pipeline como obrigatório (**Pipelines must succeed** no GitLab
   [ref:gitlab-pipeline-obrigatorio], o status check exigido no GitHub [ref:github-branch-protegida])
   e ponha o arquivo de CI no CODEOWNERS: quem tira o job na MR tira o gate.
6. Ligue o verificador do portal, que avisa quando o CI não tem um dos dois jobs. Ele vem no pacote
   gerado (`pacote/verificadores/seg_06.py`); até o instalador (F4), copie-o para `verificadores/`
   do projeto, sem alterá-lo, e acrescente o job abaixo. Até o runtime de hooks (F2), o gatilho de
   harness não se liga à mão.

   ```yaml
   lacuna-de-varredura:
     stage: travas
     image: python:3.11
     allow_failure: true
     variables:
       GIT_DEPTH: "0"
     rules:
       - if: $CI_PIPELINE_SOURCE == "merge_request_event"
     script:
       - git config --global --add safe.directory "$PWD"
       - python3 -I verificadores/seg_06.py --evento ci --base "$CI_MERGE_REQUEST_DIFF_BASE_SHA"
   ```

   Com `allow_failure: true`, o aviso fica laranja e não derruba o pipeline [ref:gitlab-allow-failure]:
   a força é `avisa`, e o gate de verdade são os dois jobs de varredura.
7. Arquivo que não vai para produção (um `Dockerfile` de exemplo, um script de documentação) sai da
   conta do verificador pelo `.seg06-ignorar`, na raiz, com a mesma forma do `.seg02-ignorar` da
   SEG-02: o caminho exato de um arquivo ou uma subpasta com `/**` no fim, com ao menos dois
   segmentos literais. A isenção vale depois que a MR que a cria entra na branch de destino. Ponha o
   `.seg06-ignorar` no CODEOWNERS.

## Exemplo

### Antes e depois

Antes, a imagem parte de uma base antiga e o código passa o nome de arquivo para o shell:

<!-- incluir: exemplos/SEG-06/antes/Dockerfile -->

<!-- incluir: exemplos/SEG-06/antes/app.py -->

Depois, a base é atual, o `pip` sai da imagem final, o processo não roda como root, e o comando é uma
lista de argumentos, sem shell:

<!-- incluir: exemplos/SEG-06/depois/Dockerfile -->

<!-- incluir: exemplos/SEG-06/depois/app.py -->

Os jobs no GitLab CI (o build e as duas varreduras):

<!-- incluir: exemplos/SEG-06/gitlab-ci.yml -->

E no GitHub Actions:

<!-- incluir: exemplos/SEG-06/github-workflow.yml -->

Rodados em 2026-11-04 com as imagens dos jobs, fixadas pelo digest, e os mesmos argumentos (o Trivy
lendo a imagem do Docker local, não do registro), os scanners reprovam o antes e passam o depois. Os
jobs não rodaram num runner do GitLab nem do GitHub:

```text
antes   trivy  : debian 10.13, Total: 42 (HIGH: 40, CRITICAL: 2); pacotes Python, Total: 4 (HIGH: 4); saída 1
antes   semgrep: dockerfile.security.missing-user, python.lang.security.audit.subprocess-shell-true; 2 findings; saída 1
depois  trivy  : alpine 3.24.3, 0 vulnerabilidades; saída 0
depois  semgrep: 0 findings; saída 0
```

O resultado do Trivy depende do banco de vulnerabilidades do dia: a mesma imagem pode reprovar
amanhã. Na primeira versão do depois (2026-11-03), com o `pip` ainda na imagem, o Trivy achou 5 vulnerabilidades
`HIGH` em bibliotecas que o `pip` embute; tirá-lo da imagem final zerou a conta.

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
O CI tem, ao lado do job de segredo, o job varredura-imagem (trivy) e o job sast (semgrep), sem
allow_failure. Não tire nenhum dos dois nem afrouxe a severidade para a MR passar; achado na imagem
se corrige na imagem base ou no pacote, achado no código se corrige no código.
```

Prompt para pôr os dois jobs num projeto que só varre segredo:

```prompt
Aplique a prática SEG-06 do portal de padrões de engenharia neste repositório.

1. Leia o Dockerfile, o app.py e o .gitlab-ci.yml. Rode
   python3 -I verificadores/seg_06.py --evento ci --base 0000000000000000000000000000000000000000
   (a base de zeros avalia o HEAD inteiro) e mostre a saída.
2. Acrescente ao .gitlab-ci.yml, só em pipeline de merge request e sem allow_failure: o job
   construir-imagem (stage build, docker:29.5.2-cli com o serviço docker:29.5.2-dind, docker login,
   build e push de $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA) e, no stage travas, os jobs varredura-imagem
   (aquasec/trivy:0.76.1, needs construir-imagem, trivy image --exit-code 1 --severity
   HIGH,CRITICAL sobre a mesma tag) e sast (semgrep/semgrep:1.182.1, semgrep scan --config p/default
   --error --metrics off .). Fixe cada imagem pela tag e pelo digest, lido com
   docker buildx imagetools inspect, e diga de onde veio cada digest.
3. Rode localmente os dois scanners com docker run, com os mesmos argumentos, sobre a imagem
   construída do Dockerfile e sobre o código. Mostre o resumo de cada um.
4. Corrija o que eles acharem: troque a imagem base por uma atual, tire da imagem final o que não roda
   em produção, rode o processo com um usuário que não é root e troque shell=True por lista de
   argumentos. Não afrouxe a severidade nem ignore achado.
5. Faça o commit, rode os dois scanners de novo e o verificador do passo 1, e mostre que os três saem
   com 0.
```

Antes de rodar, o repositório precisa ter o `Dockerfile` e o `app.py` do antes, um `.gitlab-ci.yml`
só com o job de testes, o `verificadores/seg_06.py` do pacote e o Docker.

### Por ferramenta

- **GitLab, tier Ultimate:** o resultado de Container Scanning aparece na MR e na aba Security do
  pipeline [ref:gitlab-container-scanning], e a política de aprovação de MR exige
  aprovação quando o scanner acha algo ou termina sem relatório [ref:gitlab-politicas-de-aprovacao].
- **GitHub:** o CodeQL pode substituir o Semgrep no job de SAST [ref:github-codeql]; a varredura de
  imagem fica com a `trivy-action` do Exemplo [ref:trivy-action].

## Como verificar

O mecanismo é `verificadores/seg_06.py`, com força `avisa`: ele não confere se a imagem ou o código
estão limpos (isso é o trabalho dos scanners), e sim se o CI tem os dois jobs quando o repositório
precisa deles.

- **O que ele procura.** Há lacuna de imagem quando o repositório tem `Dockerfile`, `Dockerfile.*`,
  `*.Dockerfile`, `Containerfile` ou um compose com `build:`, e o CI não cita `trivy`, `grype`,
  `container_scanning` nem `anchore/scan-action`. Há lacuna de SAST quando há código (`.py`, `.js`,
  `.ts`, `.go`, `.java` e outras extensões) e o CI não cita `semgrep`, `codeql` nem `sast` como
  palavra. Sem arquivo de CI, não há lacuna. O CI é o `.gitlab-ci.yml` da raiz, os arquivos locais
  que ele inclui (até três níveis, com os curingas `*` e `**` que o `include:local` aceita
  [ref:gitlab-include-local]) e os `.github/workflows/*.yml`. Nome dentro de comentário YAML não conta. Pastas de terceiros
  (`node_modules`, `.venv`, `vendor`), submódulos e links simbólicos ficam fora.
- **Quando avisa.** No harness, antes de o agente editar ou escrever um arquivo, comparando o disco
  com o arquivo novo contra o disco de antes; no CI, comparando o `HEAD` com `--base`. A lacuna nova
  é sempre apontada; a antiga só quando a mudança toca o CI, um `Dockerfile`, um compose ou o
  `.seg06-ignorar`, para uma MR só de código não repetir o aviso.
- **Saídas.** 0: nada a apontar. 1: uma linha por lacuna, `<arquivo de CI>:0: <motivo>`. 2: não
  conseguiu decidir, com o motivo em stderr: base ausente (clone raso; use `GIT_DEPTH: "0"`), isenção
  ampla demais, ou CI que inclui arquivo de outro projeto (`project:`, `remote:`, workflow
  reutilizável de outro repositório), que o verificador não lê. O `project:` dentro de `trigger:` não
  conta: ele dispara um pipeline em outro projeto [ref:gitlab-pipelines-downstream], que não soma jobs
  a este.
- **Os limites.** É conferência de nome: um job chamado `sast` que não roda nada passa, e uma variável
  como `SAST_DISABLED` também conta como SAST. Ele não sabe se o job tem `allow_failure`, se roda na
  MR nem se a severidade é a certa; isso fica para a revisão do arquivo de CI, sob CODEOWNERS. Não lê
  CI de outro provedor além de GitLab e GitHub Actions.
